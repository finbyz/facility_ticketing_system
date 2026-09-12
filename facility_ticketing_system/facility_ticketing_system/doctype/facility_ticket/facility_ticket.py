# Copyright (c) 2026, MAB Facilities and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, add_to_date, get_datetime, time_diff_in_seconds


class FacilityTicket(Document):
	def validate(self):
		self.set_auto_fields()
		self.set_sla_dates()
		self.validate_status_transition()
		self.add_status_change_update()
		self.validate_client_comments()

	def after_insert(self):
		self.send_creation_notification()
		self.add_initial_update()

	def on_update(self):
		if self.has_value_changed("status"):
			self.send_status_notification()
			self.handle_reopen()

	def set_auto_fields(self):
		"""Auto-populate Email Recipient, Assigned Person, Team, Priority & SLA from Sub Category"""
		if not self.sub_category:
			return

		sub = frappe.get_cached_doc("Service Sub Category", self.sub_category)

		# Email Recipient
		if sub.email_recipient:
			self.email_recipient = sub.email_recipient

		# Assigned Team
		if sub.assigned_team:
			self.assigned_team = sub.assigned_team

		# Default Priority (only if not already set by agent)
		if not self.request_priority and sub.default_priority:
			self.request_priority = sub.default_priority

		# SLA minutes
		self.resolution_sla_minutes = sub.resolution_sla_minutes or 0
		self.follow_up_sla_minutes = sub.follow_up_sla_minutes or 0
		self.second_follow_up_sla_minutes = sub.second_follow_up_sla_minutes or 0

		# Assigned Person from Level 1 Contact
		if sub.level_1_contact:
			contact = frappe.get_cached_doc("Escalation Contact", sub.level_1_contact)
			if contact.user:
				self.assigned_person = contact.user
			if contact.email_address and not self.email_recipient:
				self.email_recipient = contact.email_address

	def set_sla_dates(self):
		"""Calculate Resolution Due and Follow-up Due based on creation / reopen time"""
		if self.is_new() or self.has_value_changed("status") and self.status == "Reopened":
			base_time = now_datetime()

			if self.resolution_sla_minutes:
				self.resolution_due = add_to_date(
					base_time, minutes=self.resolution_sla_minutes, as_datetime=True
				)
			if self.follow_up_sla_minutes:
				self.follow_up_due = add_to_date(
					base_time, minutes=self.follow_up_sla_minutes, as_datetime=True
				)
			if self.second_follow_up_sla_minutes:
				second_base = self.follow_up_due or base_time
				self.second_follow_up_due = add_to_date(
					second_base, minutes=self.second_follow_up_sla_minutes, as_datetime=True
				)

			self.sla_status = "Within SLA"

	def validate_status_transition(self):
		"""Basic status transition validation"""
		if self.is_new():
			return

		old_status = self.get_db_value("status")
		if not old_status:
			return

		allowed = {
			"Open": ["In Progress", "Closed"],
			"In Progress": ["Resolved", "Open", "Closed"],
			"Resolved": ["Closed", "Reopened"],
			"Closed": ["Reopened"],
			"Reopened": ["In Progress", "Resolved", "Closed"],
		}

		if self.status != old_status and self.status not in allowed.get(old_status, []):
			frappe.throw(
				_("Cannot change status from <b>{0}</b> to <b>{1}</b>").format(
					old_status, self.status
				)
			)

	def validate_client_comments(self):
		"""Require at least one comment when moving to Resolved / Closed / Reopened"""
		if self.status in ("Resolved", "Closed", "Reopened") and not self.is_new():
			if not self.ticket_updates:
				frappe.throw(
					_("Please add Client Comments / Update before setting status to {0}").format(
						self.status
					)
				)

	def add_initial_update(self):
		"""Add system generated first update"""
		self.append(
			"ticket_updates",
			{
				"update_date": now_datetime(),
				"updated_by": frappe.session.user,
				"status_at_update": self.status,
				"comment": f"Ticket created by {frappe.session.user}",
			},
		)
		self.db_update()

	# def add_status_change_update(self):
	# 	"""Add a ticket update row when the ticket status changes."""
	# 	if self.is_new():
	# 		return

	# 	old_status = self.get_db_value("status")
	# 	if not old_status or self.status == old_status:
	# 		return

	# 	self.append(
	# 		"ticket_updates",
	# 		{
	# 			"update_date": now_datetime(),
	# 			"updated_by": frappe.session.user,
	# 			"status_at_update": self.status,
	# 			"comment": f"Status changed from {old_status} to {self.status}",
	# 		},
	# 	)
	def add_status_change_update(self):
		"""Add a ticket update row when the ticket status changes, unless the
		client already logged one for this same transition."""
		if self.is_new():
			return
		old_status = self.get_db_value("status")
		if not old_status or self.status == old_status:
			return
		for row in self.ticket_updates:
			if row.status_at_update == self.status and row.get("__islocal"):
				return
		self.append(
			"ticket_updates",
			{
				"update_date": now_datetime(),
				"updated_by": frappe.session.user,
				"status_at_update": self.status,
				"comment": f"Status changed from {old_status} to {self.status}",
			},
		)

	def handle_reopen(self):
		"""Reset SLA when ticket is reopened"""
		if self.status == "Reopened":
			self.set_sla_dates()
			self.db_set(
				{
					"resolution_due": self.resolution_due,
					"follow_up_due": self.follow_up_due,
					"second_follow_up_due": self.second_follow_up_due,
					"sla_status": "Within SLA",
				}
			)

	def send_creation_notification(self):
		"""Send email to Email Recipient on ticket creation"""
		recipients = []
		if self.email_recipient:
			recipients.append(self.email_recipient)
		if self.email_address:
			recipients.append(self.email_address)

		if not recipients:
			return

		try:
			frappe.sendmail(
				recipients=list(set(recipients)),
				subject=f"[New Ticket] {self.name} - {self.service_category} / {self.sub_category}",
				message=self.get_notification_message("created"),
				reference_doctype=self.doctype,
				reference_name=self.name,
			)
		except Exception as e:
			frappe.log_error(f"Failed to send ticket creation email: {e}", "Facility Ticket Email")

	def send_status_notification(self):
		"""Notify on status change"""
		recipients = []
		if self.email_recipient:
			recipients.append(self.email_recipient)
		if self.email_address:
			recipients.append(self.email_address)

		if not recipients:
			return

		try:
			frappe.sendmail(
				recipients=list(set(recipients)),
				subject=f"[Status Update] {self.name} → {self.status}",
				message=self.get_notification_message("status_changed"),
				reference_doctype=self.doctype,
				reference_name=self.name,
			)
		except Exception as e:
			frappe.log_error(f"Failed to send status email: {e}", "Facility Ticket Email")

	def get_notification_message(self, event):
		"""Build HTML email body"""
		return frappe.render_template(
			"""
			<p>Dear Team,</p>
			<p>Ticket <b>{{ doc.name }}</b> has been {{ event }}.</p>
			<table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse;">
				<tr><td><b>Request Type</b></td><td>{{ doc.request_type }}</td></tr>
				<tr><td><b>Customer</b></td><td>{{ doc.customer_name }}</td></tr>
				<tr><td><b>Email</b></td><td>{{ doc.email_address }}</td></tr>
				<tr><td><b>Phone</b></td><td>{{ doc.phone_number }}</td></tr>
				<tr><td><b>Location</b></td><td>{{ doc.location_details }}</td></tr>
				<tr><td><b>Building / Unit</b></td><td>{{ doc.building_name }} / {{ doc.flat_unit_no }}</td></tr>
				<tr><td><b>Category</b></td><td>{{ doc.service_category }} → {{ doc.sub_category }}</td></tr>
				<tr><td><b>Priority</b></td><td>{{ doc.request_priority }}</td></tr>
				<tr><td><b>Status</b></td><td>{{ doc.status }}</td></tr>
				<tr><td><b>Description</b></td><td>{{ doc.description }}</td></tr>
				<tr><td><b>Resolution Due</b></td><td>{{ doc.resolution_due or '-' }}</td></tr>
			</table>
			<p>Please take necessary action.</p>
			<p>Regards,<br>MAB Ticketing System</p>
			""",
			{"doc": self, "event": event},
		)


@frappe.whitelist()
def get_sub_categories(service_category):
	"""API to fetch active sub categories for a given service category"""
	if not service_category:
		return []

	return frappe.get_all(
		"Service Sub Category",
		filters={"service_category": service_category, "is_active": 1},
		fields=["name", "sub_category_name", "email_recipient", "default_priority",
				"resolution_sla_minutes", "follow_up_sla_minutes", "second_follow_up_sla_minutes", "assigned_team"],
		order_by="sub_category_name",
	)


def check_sla_breaches():
	"""Scheduled job – runs every 10 minutes to check SLA status"""
	now = now_datetime()

	open_tickets = frappe.get_all(
		"Facility Ticket",
		filters={"status": ["in", ["Open", "In Progress", "Reopened"]]},
		fields=["name", "resolution_due", "follow_up_due", "second_follow_up_due", "sla_status"],
	)

	for t in open_tickets:
		new_status = "Within SLA"

		if t.resolution_due and get_datetime(t.resolution_due) < now:
			new_status = "Resolution Overdue"
		elif t.second_follow_up_due and get_datetime(t.second_follow_up_due) < now:
			new_status = "Second Follow-up Overdue"
		elif t.follow_up_due and get_datetime(t.follow_up_due) < now:
			new_status = "Follow-up Overdue"

		if new_status != t.sla_status:
			frappe.db.set_value(
				"Facility Ticket",
				t.name,
				"sla_status",
				new_status,
				update_modified=False,
			)

			# Optional: escalate / notify on breach
			if new_status in ("Resolution Overdue", "Follow-up Overdue", "Second Follow-up Overdue"):
				_notify_sla_breach(t.name, new_status)



def _notify_sla_breach(ticket_name, breach_type):
	"""Send breach notification"""
	doc = frappe.get_doc("Facility Ticket", ticket_name)
	
	recipients = []
	if doc.email_recipient:
		recipients.append(doc.email_recipient)
	if doc.email_address:
		recipients.append(doc.email_address)

	if doc.sub_category:
		sub = frappe.get_cached_doc("Service Sub Category", doc.sub_category)
		if breach_type == "Follow-up Overdue" and sub.level_1_contact:
			l1 = frappe.get_cached_doc("Escalation Contact", sub.level_1_contact)
			if l1.email_address:
				recipients.append(l1.email_address)
		elif breach_type == "Second Follow-up Overdue" and sub.level_2_contact:
			l2 = frappe.get_cached_doc("Escalation Contact", sub.level_2_contact)
			if l2.email_address:
				recipients.append(l2.email_address)
		elif breach_type == "Resolution Overdue" and sub.level_2_contact:
			l2 = frappe.get_cached_doc("Escalation Contact", sub.level_2_contact)
			if l2.email_address:
				recipients.append(l2.email_address)

	recipients = list(set(recipients))
	if not recipients:
		return

	try:
		frappe.sendmail(
			recipients=recipients,
			subject=f"[SLA BREACH] {doc.name} - {breach_type}",
			message=f"""
			<p><b>SLA Breach Alert</b></p>
			<p>Ticket <b>{doc.name}</b> has breached its {breach_type}.</p>
			<p>Customer: {doc.customer_name}<br>
			Category: {doc.service_category} / {doc.sub_category}<br>
			Priority: {doc.request_priority}<br>
			Due: {doc.resolution_due if breach_type == 'Resolution Overdue' else doc.second_follow_up_due if breach_type == 'Second Follow-up Overdue' else doc.follow_up_due}</p>
			<p>Please take immediate action.</p>
			""",
			reference_doctype=doc.doctype,
			reference_name=doc.name,
		)
	except Exception as e:
		frappe.log_error(str(e), "SLA Breach Notification")

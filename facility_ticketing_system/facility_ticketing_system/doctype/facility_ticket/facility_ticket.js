// Copyright (c) 2026, MAB Facilities and contributors
// For license information, please see license.txt

frappe.ui.form.on("Facility Ticket", {
	property_community(frm) {
        frm.set_value("service_category", "");

        if (!frm.doc.property_community) {
            frm.set_query("service_category", function () {
                return {
                    filters: {
                        name: ["in", []]
                    }
                };
            });
            return;
        }

        frappe.db.get_doc("Property", frm.doc.property_community).then(property => {
            const service_categories = (property.services || [])
                .map(row => row.service_category)
                .filter(Boolean);

            frm.set_query("service_category", function () {
                return {
                    filters: {
                        name: ["in", service_categories]
                    }
                };
            });
        });
    },
	refresh(frm) {
		// Set indicators
		if (frm.doc.sla_status === "Resolution Overdue") {
			frm.dashboard.set_headline_alert(__("Resolution SLA Breached"), "red");
		} else if (frm.doc.sla_status === "Follow-up Overdue") {
			frm.dashboard.set_headline_alert(__("Follow-up SLA Overdue"), "orange");
		}

		// Quick action buttons — each opens a comment dialog before changing status
		if (!frm.is_new() && ["Open", "Reopened"].includes(frm.doc.status)) {
			frm.add_custom_button(__("Start Work"), () => {
				show_status_update_dialog(frm, "In Progress");
			}, __("Actions"));
		}

		if (!frm.is_new() && frm.doc.status === "In Progress") {
			frm.add_custom_button(__("Mark Resolved"), () => {
				show_status_update_dialog(frm, "Resolved");
			}, __("Actions"));
		}

		if (!frm.is_new() && frm.doc.status === "Resolved") {
			frm.add_custom_button(__("Close Ticket"), () => {
				show_status_update_dialog(frm, "Closed");
			}, __("Actions"));
		}

		if (!frm.is_new() && frm.doc.status === "Closed") {
			frm.add_custom_button(__("Reopen"), () => {
				show_status_update_dialog(frm, "Reopened");
			}, __("Actions"));
		}
	},

	service_category(frm) {
		frm.set_value("sub_category", "");
		frm.set_value("email_recipient", "");
		frm.set_value("assigned_person", "");
		frm.set_value("assigned_team", "");
		frm.set_value("resolution_sla_minutes", "");
		frm.set_value("follow_up_sla_minutes", "");

		if (frm.doc.service_category) {
			frm.set_query("sub_category", function () {
				return {
					filters: {
						service_category: frm.doc.service_category,
						is_active: 1,
					},
				};
			});
		}
	},

	sub_category(frm) {
		if (!frm.doc.sub_category) return;

		frappe.db.get_doc("Service Sub Category", frm.doc.sub_category).then((sub) => {
			if (sub.email_recipient) frm.set_value("email_recipient", sub.email_recipient);
			if (sub.assigned_team) frm.set_value("assigned_team", sub.assigned_team);
			if (sub.default_priority && !frm.doc.request_priority) {
				frm.set_value("request_priority", sub.default_priority);
			}
			if (sub.resolution_sla_minutes) frm.set_value("resolution_sla_minutes", sub.resolution_sla_minutes);
			if (sub.follow_up_sla_minutes) frm.set_value("follow_up_sla_minutes", sub.follow_up_sla_minutes);

			if (sub.level_1_contact) {
				frappe.db.get_value(
					"Escalation Contact",
					sub.level_1_contact,
					["user", "email_address"],
					(r) => {
						if (r && r.user) {
							frm.set_value("assigned_person", r.user);
						} else if (r && r.email_address && !frm.doc.email_recipient) {
							frm.set_value("email_recipient", r.email_address);
						}
					}
				);
			}
		});
	},

	status(frm) {
		if (["Resolved", "Closed", "Reopened"].includes(frm.doc.status)) {
			if (!frm.doc.ticket_updates || frm.doc.ticket_updates.length === 0) {
				frappe.msgprint({
					title: __("Comment Required"),
					indicator: "orange",
					message: __("Please add at least one Client Comment / Update before changing status to {0}.", [frm.doc.status]),
				});
			}
		}
	},
});

// Child table: auto set updated_by when a row is added manually via "Add row"
frappe.ui.form.on("Ticket Update", {
	ticket_updates_add(frm, cdt, cdn) {
		frappe.model.set_value(cdt, cdn, "updated_by", frappe.session.user);
		frappe.model.set_value(cdt, cdn, "status_at_update", frm.doc.status);
		frappe.model.set_value(cdt, cdn, "update_date", frappe.datetime.now_datetime());
	},
});

// Shared popup used by every action button
function show_status_update_dialog(frm, new_status) {
	let d = new frappe.ui.Dialog({
		title: __("Update Ticket — {0}", [new_status]),
		fields: [
			{
				fieldname: "comment",
				fieldtype: "Small Text",
				label: __("Client Comments / Update"),
				reqd: 1,
			},
		],
		primary_action_label: __("Save"),
		primary_action(values) {
			frm.add_child("ticket_updates", {
				update_date: frappe.datetime.now_datetime(),
				updated_by: frappe.session.user,
				status_at_update: new_status,
				comment: values.comment,
			});
			frm.refresh_field("ticket_updates");
			frm.set_value("status", new_status);

			frm.save().then(() => {
				d.hide();
			}).catch(() => {
				// leave dialog open so the user doesn't lose their comment on a validation error
			});
		},
	});
	d.show();
}
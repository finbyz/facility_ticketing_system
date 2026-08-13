// Copyright (c) 2026, MAB Facilities and contributors
// For license information, please see license.txt

frappe.listview_settings["Facility Ticket"] = {
	add_fields: ["status", "request_priority", "sla_status", "service_category", "assigned_person"],

	get_indicator(doc) {
		const status_colors = {
			Open: "blue",
			"In Progress": "orange",
			Resolved: "green",
			Closed: "gray",
			Reopened: "red",
		};

		// Override with SLA status if breached
		if (doc.sla_status === "Resolution Overdue") {
			return [__("SLA Breached"), "red", "sla_status,=,Resolution Overdue"];
		}
		if (doc.sla_status === "Follow-up Overdue") {
			return [__("Follow-up Overdue"), "orange", "sla_status,=,Follow-up Overdue"];
		}

		return [__(doc.status), status_colors[doc.status] || "gray", `status,=,${doc.status}`];
	},

	onload(listview) {
		// Quick filters
		listview.page.add_inner_button(__("My Tickets"), function () {
			listview.filter_area.add([
				["Facility Ticket", "assigned_person", "=", frappe.session.user],
			]);
		});

		listview.page.add_inner_button(__("SLA Breached"), function () {
			listview.filter_area.add([
				["Facility Ticket", "sla_status", "=", "Resolution Overdue"],
			]);
		});
	},

	formatters: {
		request_priority(value) {
			const colors = {
				Critical: "red",
				High: "orange",
				Medium: "blue",
				Low: "green",
			};
			return `<span class="indicator-pill ${colors[value] || "gray"} filterable">${value}</span>`;
		},
	},
};

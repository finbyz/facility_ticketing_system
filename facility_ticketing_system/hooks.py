app_name = "facility_ticketing_system"
app_title = "Facility Ticketing System"
app_publisher = "Finbyz Tech Pvt. Ltd"
app_description = "MAB Facility Ticketing System"
app_email = "info@finbyz.tech"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "facility_ticketing_system",
# 		"logo": "/assets/facility_ticketing_system/logo.png",
# 		"title": "Facility Ticketing System",
# 		"route": "/facility_ticketing_system",
# 		"has_permission": "facility_ticketing_system.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/facility_ticketing_system/css/facility_ticketing_system.css"
# app_include_js = "/assets/facility_ticketing_system/js/facility_ticketing_system.js"

# include js, css files in header of web template
# web_include_css = "/assets/facility_ticketing_system/css/facility_ticketing_system.css"
# web_include_js = "/assets/facility_ticketing_system/js/facility_ticketing_system.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "facility_ticketing_system/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_list_js = {
    "Facility Ticket": "public/js/facility_ticket_list.js"
}# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "facility_ticketing_system/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "facility_ticketing_system.utils.jinja_methods",
# 	"filters": "facility_ticketing_system.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "facility_ticketing_system.install.before_install"
# after_install = "facility_ticketing_system.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "facility_ticketing_system.uninstall.before_uninstall"
# after_uninstall = "facility_ticketing_system.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "facility_ticketing_system.utils.before_app_install"
# after_app_install = "facility_ticketing_system.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "facility_ticketing_system.utils.before_app_uninstall"
# after_app_uninstall = "facility_ticketing_system.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "facility_ticketing_system.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "facility_ticketing_system.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------
scheduler_events = {
    "cron": {
        "*/10 * * * *": [
            "facility_ticketing_system.facility_ticketing_system.doctype.facility_ticket.facility_ticket.check_sla_breaches"
        ]
    }
}
# scheduler_events = {
# 	"all": [
# 		"facility_ticketing_system.tasks.all"
# 	],
# 	"daily": [
# 		"facility_ticketing_system.tasks.daily"
# 	],
# 	"hourly": [
# 		"facility_ticketing_system.tasks.hourly"
# 	],
# 	"weekly": [
# 		"facility_ticketing_system.tasks.weekly"
# 	],
# 	"monthly": [
# 		"facility_ticketing_system.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "facility_ticketing_system.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "facility_ticketing_system.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "facility_ticketing_system.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "facility_ticketing_system.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["facility_ticketing_system.utils.before_request"]
# after_request = ["facility_ticketing_system.utils.after_request"]

# Job Events
# ----------
# before_job = ["facility_ticketing_system.utils.before_job"]
# after_job = ["facility_ticketing_system.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"facility_ticketing_system.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []


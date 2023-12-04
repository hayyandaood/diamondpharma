from . import __version__ as app_version

app_name = "diamondpharma"
app_title = "Diamondpharma"
app_publisher = "oaktc"
app_description = "diamondpharma customizations"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "waelhammoudi71@gmain.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/diamondpharma/css/diamondpharma.css"
# app_include_js = "/assets/diamondpharma/js/diamondpharma.js"

# include js, css files in header of web template
# web_include_css = "/assets/diamondpharma/css/diamondpharma.css"
# web_include_js = "/assets/diamondpharma/js/diamondpharma.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "diamondpharma/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_js = {"Work Order": "public/js/custom_work_order.js"}
doctype_js = {"Job Card": "public/js/custom_jobcard.js"}
doctype_js = {"Stock Entry": "public/js/custom_stockentry.js"}
# doctype_js = {"Stock Entry": "public/js/custom_stock_entry.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_list_js = {"Batch": "public/js/custom_batch_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

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

# Installation
# ------------

# before_install = "diamondpharma.install.before_install"
# after_install = "diamondpharma.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "diamondpharma.uninstall.before_uninstall"
# after_uninstall = "diamondpharma.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "diamondpharma.notifications.get_notification_config"

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

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }
override_doctype_class = {
    #    "Job Card": "diamondpharma.diamondpharma.jobcard.DiamondpharmaJobCard",
    "Work Order": "diamondpharma.diamondpharma.workorder.DiamondpharmaWorkOrder",
    "Stock Entry": "diamondpharma.diamondpharma.stockentry.StockEntry",
    "Salary Slip": "diamondpharma.diamondpharma.api.SalarySlipOverride",
    "Leave Application": "diamondpharma.diamondpharma.leave_application_extension.DiamondpharmaLeaveApplication",
    #    "Budget": "diamondpharma.diamondpharma.multi_dimensional_budgeting.MultiBudget",
}

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
# doc_events = {
# 	"JobCard": {
# 			"on_submit": "diamondpharma.overrides.jobcard.DiamondpharmaJobCard",
# 	}
# }
#	}

doc_events = {"Salary Slip" : {"validate": "diamondpharma.diamondpharma.api.get_totals_validate"}}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"diamondpharma.tasks.all"
# 	],
# 	"daily": [
# 		"diamondpharma.tasks.daily"
# 	],
# 	"hourly": [
# 		"diamondpharma.tasks.hourly"
# 	],
# 	"weekly": [
# 		"diamondpharma.tasks.weekly"
# 	]
# 	"monthly": [
# 		"diamondpharma.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "diamondpharma.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "diamondpharma.event.get_events"
# }

override_whitelisted_methods = {
    "erpnext.manufacturing.doctype.work_order.work_order.make_work_order": "diamondpharma.diamondpharma.whitelisted.make_work_order",
    # "erpnext.manufacturing.doctype.work_order.work_order.make_stock_entry": "diamondpharma.diamondpharma.whitelisted.make_stock_entry",
}

#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "diamondpharma.task.get_dashboard_data"
# }

override_doctype_dashboards = {
    "Job Card": "diamondpharma.diamondpharma.dashboard_overrides.custom_jobcard_get_data",
    "Work Order": "diamondpharma.diamondpharma.dashboard_overrides.custom_workorder_get_data",
}

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Monkey patching
# ------------------
# Imports specific to the patches

# from diamondpharma.diamondpharma import multi_dimensional_budgeting
# from erpnext.accounts.doctype.budget import budget

# Replace frappe function with custom function
# Monkey patch the new function onto the existing function
# budget.validate_expense_against_budget = (
#    multi_dimensional_budgeting.new_validate_expense_against_budget
# )


# User Data Protection
# --------------------

user_data_fields = [
    {
        "doctype": "{doctype_1}",
        "filter_by": "{filter_by}",
        "redact_fields": ["{field_1}", "{field_2}"],
        "partial": 1,
    },
    {
        "doctype": "{doctype_2}",
        "filter_by": "{filter_by}",
        "partial": 1,
    },
    {
        "doctype": "{doctype_3}",
        "strict": False,
    },
    {"doctype": "{doctype_4}"},
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"diamondpharma.auth.validate"
# ]

# Translation
# --------------------------------

# Make link fields search translated document names for these DocTypes
# Recommended only for DocTypes which have limited documents with untranslated names
# For example: Role, Gender, etc.
# translated_search_doctypes = []
#fixtures = [
#    "Manufacturing Custom Settings",
#    "Custom Field",
#    "Property Setter",
#    "Accounting Dimension",
#    "Item Attribute",
#    {"doctype": "Workspace", "filters": [["module", "like", "Diamondpharma"]]},
#]

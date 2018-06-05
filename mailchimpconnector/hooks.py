# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "mailchimpconnector"
app_title = "MailChimpConnector"
app_publisher = "libracore"
app_description = "Connector to sync ERPNext contacts and campai"
app_icon = "octicon octicon-mail"
app_color = "#46b8e3"
app_email = "info@libracore.com"
app_license = "AGPL"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/mailchimpconnector/css/mailchimpconnector.css"
# app_include_js = "/assets/mailchimpconnector/js/mailchimpconnector.js"

# include js, css files in header of web template
# web_include_css = "/assets/mailchimpconnector/css/mailchimpconnector.css"
# web_include_js = "/assets/mailchimpconnector/js/mailchimpconnector.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "mailchimpconnector.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "mailchimpconnector.install.before_install"
# after_install = "mailchimpconnector.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "mailchimpconnector.notifications.get_notification_config"

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
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"mailchimpconnector.tasks.all"
# 	],
# 	"daily": [
# 		"mailchimpconnector.tasks.daily"
# 	],
# 	"hourly": [
# 		"mailchimpconnector.tasks.hourly"
# 	],
# 	"weekly": [
# 		"mailchimpconnector.tasks.weekly"
# 	]
# 	"monthly": [
# 		"mailchimpconnector.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "mailchimpconnector.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "mailchimpconnector.event.get_events"
# }


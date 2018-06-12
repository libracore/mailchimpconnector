# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"module_name": "MailChimpConnector",
			"color": "#46b8e3",
			"icon": "octicon octicon-mail",
			"type": "module",
			"label": _("MailChimpConnector"),
            "hidden": 1
		}
	]

# -*- coding: utf-8 -*-
# Copyright (c) 2017-2018, libracore and contributors
# License: AGPL v3. See LICENCE
from __future__ import unicode_literals
from frappe import _

def get_data():
    return[
        {
            "label": _("Sync"),
            "icon": "octicon octicon-mail",
            "items": [
                   {
                       "type": "page",
                       "name": "sync_mailchimp",
                       "label": _("Sync MailChimp"),
                       "description": _("Sync MailChimp")
                   },
		   {
                       "type": "doctype",
                       "name": "MailChimpConnector Log",
                       "label": _("MailChimpConnector Log"),
                       "description": _("MailChimpConnector Log")
                   }
            ]
        },
        {
            "label": _("Settings"),
            "icon": "octicon octicon-tools",
            "items": [
                   {
                       "type": "doctype",
                       "name": "MailChimpConnector Settings",
                       "label": _("MailChimpConnector Settings"),
                       "description": _("MailChimpConnector Settings")
                   }
            ]
        }
    ]

# -*- coding: utf-8 -*-
# Copyright (c) 2017-2018, libracore and contributors
# License: AGPL v3. See LICENCE

# import definitions
from __future__ import unicode_literals
import frappe
from frappe import throw, _
import json
import base64
import requests
from requests.auth import HTTPBasicAuth
try:
    from urllib import request as http
except ImportError:
    import urllib2 as http
from datetime import datetime

# execute API function
def execute(host, api_token, payload):  
    try:
        
        response = requests.request(method='GET',
            url=host,
            json=json.dumps(payload).encode(),
            auth=HTTPBasicAuth("MailChimpConnector", api_token))
        
        status=response.status_code
        text=response.text
        
        return text
    except:
        #frappe.log_error("Execution of http request failed. Please check host and API token.")
        frappe.throw("Execution of http request failed. Please check host and API token.")
        
@frappe.whitelist()
def get_lists():
    config = frappe.get_single("MailChimpConnector Settings")
    
    if not config.host or not config.api_key:
        frappe.throw( _("No configuration found. Please make sure that there is a MailChimpConnector configuration") )
    
    
    results = execute(config.host + "/lists", config.api_key, None)
    frappe.throw(results)
    
    return { 'lists': ["List 1", "List 2"], 'message': "Done" }

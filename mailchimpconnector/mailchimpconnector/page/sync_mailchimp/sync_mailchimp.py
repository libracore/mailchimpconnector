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
import hashlib

# execute API function
def execute(host, api_token, payload, verify_ssl=True, method="GET"):  
    try:
        response = requests.request(
            method=method,
            url=host,
            json=json.dumps(payload).encode(),
            auth=HTTPBasicAuth("MailChimpConnector", api_token),
            verify=verify_ssl)
        
        status=response.status_code
        text=response.text
        
        return text
    except Exception as e:
        #frappe.log_error("Execution of http request failed. Please check host and API token.")
        frappe.throw("Execution of http request failed. Please check host and API token. ({0})".format(e))

# execute API function
def execute_put(host, api_token, payload, verify_ssl=True):  
    try:
        response = requests.put(
            url=host,
            json=json.dumps(payload).encode(),
            auth=HTTPBasicAuth("MailChimpConnector", api_token),
            verify=verify_ssl)
        
        status=response.status_code
        text=response.text
        
        return text
    except Exception as e:
        #frappe.log_error("Execution of http request failed. Please check host and API token.")
        frappe.throw("Execution of http request failed. Please check host and API token. ({0})".format(e))
        
@frappe.whitelist()
def get_lists():
    config = frappe.get_single("MailChimpConnector Settings")
    
    if not config.host or not config.api_key:
        frappe.throw( _("No configuration found. Please make sure that there is a MailChimpConnector configuration") )
    
    if config.verify_ssl != 1:
        verify_ssl = False
    else:
        verify_ssl = True
    raw = execute(config.host + "/lists?fields=lists.name,lists.id", config.api_key, 
        None, verify_ssl)
    results = json.loads(raw)
        
    return { 'lists': results['lists'] }

@frappe.whitelist()
def get_members(list_id):
    config = frappe.get_single("MailChimpConnector Settings")
    
    if not config.host or not config.api_key:
        frappe.throw( _("No configuration found. Please make sure that there is a MailChimpConnector configuration") )
    
    if config.verify_ssl != 1:
        verify_ssl = False
    else:
        verify_ssl = True
    url = "{0}/lists/{1}/members?fields=members.id,members.email_address,members.status".format(
        config.host, list_id)  
    raw = execute(url, config.api_key, None, verify_ssl)
    results = json.loads(raw)
    return { 'members': results['members'] }

@frappe.whitelist()
def sync_contacts(list_id):
    # get settings
    config = frappe.get_single("MailChimpConnector Settings")
    
    if not config.host or not config.api_key:
        frappe.throw( _("No configuration found. Please make sure that there is a MailChimpConnector configuration") )    
    if config.verify_ssl != 1:
        verify_ssl = False
    else:
        verify_ssl = True
    
    # prepare local contacts: all contacts with an email
    erp_contacts = frappe.get_list('Contact', 
        filters={'email_id': ['LIKE', u'%@%.%']}, 
        fields=["email_id", "first_name", "last_name", "unsubscribed"])
    
    #frappe.throw(erp_contacts)
        
    # sync
    for contact in erp_contacts:
        # compute mailchimp id (md5 hash of lower-case email)
        mc_id = hashlib.md5(contact.email_id.lower()).hexdigest()
        # try to get this contact
        #url = "{0}/lists/{1}/members/{2}".format(
        #    config.host, list_id, mc_id)  
        #try:
        #    raw = execute(url, config.api_key, None, verify_ssl)
        #    results = json.loads(raw)
        #except:
        #    # this contact did not exist, create
        url = "{0}/lists/{1}/members/{2}".format(
            config.host, list_id, mc_id)  
        if contact.unsubscribed == 1:
            status = "unsubscribed"
        else:
            status = "subscribed"
        contact_object = {
            'email_address': contact.email_id,
            'status': status,
            'merge_fields': {
                'FNAME': contact.first_name, 
                'LNAME': contact.last_name 
            }
        }
        #payload = json.dumps(contact_object)
        #raw = execute(host=url, api_token=config.api_key, 
        #    payload=contact_object, verify_ssl=verify_ssl, method="PUT")
        raw = execute_put(host=url, api_token=config.api_key, 
            payload=contact_object, verify_ssl=verify_ssl)
            
        frappe.throw(raw)
    
    
    url = "{0}/lists/{1}/members?fields=members.id,members.email_address,members.status".format(
        config.host, list_id)  
    raw = execute(url, config.api_key, None, verify_ssl)
    results = json.loads(raw)
    return { 'members': results['members'] }

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
from frappe.utils.background_jobs import enqueue

# execute API function
def execute(host, api_token, payload, verify_ssl=True, method="GET"):  
    try:
        response = requests.request(
            method=method,
            url=host,
            json=payload,
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
def enqueue_sync_contacts(list_id):
    kwargs={
          'list_id': list_id
        }
    enqueue("mailchimpconnector.mailchimpconnector.page.sync_mailchimp.sync_mailchimp.sync_contacts",
        queue='long',
        timeout=1500,
        **kwargs)
    frappe.msgprint( _("Queued for syncing. It may take a few minutes to an hour."))
    return
    
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
    
    if not erp_contacts:
        frappe.msgprint( _("No contacts found") )
        return
        
    # sync
    for contact in erp_contacts:
        # compute mailchimp id (md5 hash of lower-case email)
        mc_id = hashlib.md5(contact.email_id.lower()).hexdigest()
        url = "{0}/lists/{1}/members/{2}".format(
            config.host, list_id, mc_id)  
        if contact.unsubscribed == 1:
            status = "unsubscribed"
        else:
            status = "subscribed"
        contact_object = {
            'id': mc_id,
            'email_address': contact.email_id,
            'status': status,
            'merge_fields': {
                'FNAME': contact.first_name, 
                'LNAME': contact.last_name 
            }
        }
        raw = execute(host=url, api_token=config.api_key, 
            payload=contact_object, verify_ssl=verify_ssl, method="PUT")    
    
    url = "{0}/lists/{1}/members?fields=members.id,members.email_address,members.status".format(
        config.host, list_id)  
    raw = execute(url, config.api_key, None, verify_ssl)
    results = json.loads(raw)
    frappe.log_error("Sync contacts done")
    return { 'members': results['members'] }

@frappe.whitelist()
def get_campaigns(list_id):
    config = frappe.get_single("MailChimpConnector Settings")
    
    if not config.host or not config.api_key:
        frappe.throw( _("No configuration found. Please make sure that there is a MailChimpConnector configuration") )
    
    if config.verify_ssl != 1:
        verify_ssl = False
    else:
        verify_ssl = True
    url = "{0}/campaigns?fields=campaigns.id,campaigns.status,campaigns.settings.title".format(
        config.host, list_id)  
    raw = execute(url, config.api_key, None, verify_ssl, method="GET")
    results = json.loads(raw)
    for campaign in results['campaigns']:
        try:
            erp_campaign = frappe.get_doc("Campaign", campaign['settings']['title'])
            # update if applicable
            
        except:
            # erp does not know this campaignyet, create
            new_campaign = frappe.get_doc({'doctype': 'Campaign'})
            new_campaign.campaign_name = campaign['settings']['title']
            new_campaign.insert()
            
    return { 'campaigns': results['campaigns'] }

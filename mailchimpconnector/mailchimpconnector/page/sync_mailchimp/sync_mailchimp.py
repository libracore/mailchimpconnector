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
        if status not in [200, 404]:
            frappe.log_error("Unexpected MailChimp response: http {method} {host} response {status} with message {text} on payload {payload}".format(
                status=status,text=text, payload=payload, method=method, host=host))
        if status == 404:
            return None
        
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
def get_members(list_id, count=10000):
    config = frappe.get_single("MailChimpConnector Settings")
    
    if not config.host or not config.api_key:
        frappe.throw( _("No configuration found. Please make sure that there is a MailChimpConnector configuration") )
    
    if config.verify_ssl != 1:
        verify_ssl = False
    else:
        verify_ssl = True
    url = "{0}/lists/{1}/members?members.email_address,members.status&count={2}".format(
        config.host, list_id, count)  
    raw = execute(host=url, api_token=config.api_key, payload=None, verify_ssl=verify_ssl)
    results = json.loads(raw)
    return { 'members': results['members'] }

@frappe.whitelist()
def enqueue_sync_contacts(list_id, mailchimp_as_master=0):
    add_log(title= _("Starting sync"), 
       description= ( _("Starting to sync contacts to {0}")).format(list_id),
       status="Running")
       
    kwargs={
          'list_id': list_id,
          'mailchimp_as_master': mailchimp_as_master
        }
    enqueue("mailchimpconnector.mailchimpconnector.page.sync_mailchimp.sync_mailchimp.sync_contacts",
        queue='long',
        timeout=15000,
        **kwargs)
    frappe.msgprint( _("Queued for syncing. It may take a few minutes to an hour."))
    return
    
def sync_contacts(list_id, mailchimp_as_master=0):
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
        fields=["name", "email_id", "first_name", "last_name", "unsubscribed"])
    
    if not erp_contacts:
        frappe.msgprint( _("No contacts found") )
        return
        
    # sync
    contact_written = []
    for contact in erp_contacts:
        # compute mailchimp id (md5 hash of lower-case email)
        mc_id = hashlib.md5(contact.email_id.lower()).hexdigest()
        # load subscription status from mailchimp if it is set as master
        # default is unsubscribed
        contact_status="unsubscribed"
        flag_create = False
        if "{0}".format(mailchimp_as_master) == "1":
            url = "{0}/lists/{1}/members/{2}".format(
                config.host, list_id, mc_id)
            raw = execute(host=url, api_token=config.api_key, 
                verify_ssl=verify_ssl, method="GET", payload=None)
            if raw:
                try:
                    results = json.loads(raw)
                    contact_status=results['status']
                except:
                    # default is unsubscribed
                    contact_status="unsubscribed"
                # write status to ERP
                c = frappe.get_doc("Contact", contact.name)
                if contact_status == "unsubscribed":
                    c.unsubscribed = 1
                else:
                    c.unsubscribed = 0
                c.save()
            else:
                # contact not found on MailChimp, take value from ERPNext
                if contact.unsubscribed == 1:
                    contact_status = "unsubscribed"
                else:
                    contact_status = "subscribed"
                # mark for creation
                flag_create = True
        else:
            if contact.unsubscribed == 1:
                contact_status = "unsubscribed"
            else:
                contact_status = "subscribed"

        if flag_create:
            url = "{0}/lists/{1}/members/".format(config.host, list_id)
            method="POST"
        else:
            url = "{0}/lists/{1}/members/{2}".format(config.host, list_id, mc_id)  
            method="PUT"

        contact_object = {
            "email_address": contact.email_id,
            "status": contact_status,
            "merge_fields": {
                "FNAME": contact.first_name or "", 
                "LNAME": contact.last_name or ""
            }
        }
        
        raw = execute(host=url, api_token=config.api_key, 
            payload=contact_object, verify_ssl=verify_ssl, method=method)
        contact_written.append(contact.email_id)
    
    url = "{0}/lists/{1}/members?fields=members.id,members.email_address,members.status".format(
        config.host, list_id)  
    raw = execute(url, config.api_key, None, verify_ssl)
    results = json.loads(raw)
    add_log(title= _("Sync complete"), 
       description= ( _("Sync of contacts to {0} completed.\n{1}")).format(list_id, ",".join(contact_written)),
       status="Completed")
    return { 'members': results['members'] }

def get_status_from_mailchimp(config, list_id, contact_name, mc_id):
    url = "{0}/lists/{1}/members/{2}".format(
            config.host, list_id, mc_id)  
            
@frappe.whitelist()
def enqueue_get_campaigns(list_id):
    add_log(title= _("Starting sync"), 
       description=( _("Starting to sync campaigns from {0}")).format(list_id),
       status="Running")
       
    kwargs={
          'list_id': list_id
        }
    enqueue("mailchimpconnector.mailchimpconnector.page.sync_mailchimp.sync_mailchimp.get_campaigns",
        queue='long',
        timeout=15000,
        **kwargs)
    frappe.msgprint( _("Queued for syncing. It may take a few minutes to an hour."))
    return
    
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
         
    add_log(title= _("Sync complete"), 
       description= ( _("Sync of campaigns from {0} completed.")).format(list_id),
       status="Completed")
    return { 'campaigns': results['campaigns'] }

def add_log(title, description, status="OK"):
    new_log = frappe.get_doc({'doctype': 'MailChimpConnector Log'})
    new_log.title = title
    new_log.description = description
    new_log.status = status
    new_log.date = datetime.now()
    new_log.insert()
    return

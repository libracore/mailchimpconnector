## MailChimpConnector

Connector to sync ERPNext contacts and campaigns

Disclaimer: 

* ERPNext is a trademark by Frappe Ltd. Refer to [https://erpnext.org](https://erpnext.org)
* MailChimp is a trademark by MailChimp. Refer to [https://mailchimp.com](https://mailchimp.com)
* This integration module is created and maintained by libracore. Refer to [https://libracore.com](https://libracore.com)

### License

AGPL

### Installation

The MailChimpConnector is based on ERPNext. Make sure to have a working Frappe/ERPNext server running.

Install with 

    $ cd /home/frappe/frappe-bench
    $ bench get-app https://github.com/libracore/mailchimpconnector.git
    $ bench install-app mailchimpconnector

### Configuration

After the installation, you will find the app listed under the help menu. 
To configure, type "MailChimpConnector Settings" in the awesome bar. Enter host and key and save. 
If you want, extend your custom merge fields.

### Use

To use the connector, type "Open Sync MailChimp" in the awesome bar. 
Select which list you want to sync to and hit sync.

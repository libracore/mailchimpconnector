frappe.pages['sync_mailchimp'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Sync MailChimp'),
		single_column: true
	});

	frappe.sync_mailchimp.make(page);
	frappe.sync_mailchimp.run();
    
    // add the application reference
    frappe.breadcrumbs.add("MailChimpConnector");
}

frappe.sync_mailchimp = {
	start: 0,
	make: function(page) {
		var me = frappe.sync_mailchimp;
		me.page = page;
		me.body = $('<div></div>').appendTo(me.page.main);
		var data = "";
		$(frappe.render_template('sync_mailchimp', data)).appendTo(me.body);
        
		// attach button handlers
		this.page.main.find(".btn-parse-file").on('click', function() {
			
			frappe.call({
				method: 'mailchimpconnector.mailchimpconnector.page.sync_mailchimp.sync_mailchimp.get_lists',
				/*args: {
					content: content
				},*/
				callback: function(r) {
					if (r.message) {
						var parent = page.main.find(".insert-log-messages").empty();
						$('<p>' + __(r.message.message) + '</p>').appendTo(parent);
					} 
				}
			}); 

		});
	},
	run: function() {

	}
}

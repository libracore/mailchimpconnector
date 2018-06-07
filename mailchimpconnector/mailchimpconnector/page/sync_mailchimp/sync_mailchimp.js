frappe.pages['sync_mailchimp'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Sync MailChimp'),
		single_column: true
	});

	frappe.sync_mailchimp.make(page);
	frappe.sync_mailchimp.run(page);
    
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
			// get selected list
			var list_id = document.getElementById("mailchimp_lists").value;
			get_mailchimp_members(page, list_id);

		});
        this.page.main.find(".btn-upload-contacts").on('click', function() {	
            // get selected list
			var list_id = document.getElementById("mailchimp_lists").value;
			sync_contacts(page, list_id);
        });
        
	},
	run: function(page) {
        // load MailChimp lists
        load_mailchimp_lists(page);
	}
}

function load_mailchimp_lists(page) {
    frappe.call({
        method: 'mailchimpconnector.mailchimpconnector.page.sync_mailchimp.sync_mailchimp.get_lists',
        callback: function(r) {
            if (r.message) {
                var select = document.getElementById("mailchimp_lists");
                for (var i = 0; i < r.message.lists.length; i++) {
                    var opt = document.createElement("option");
                    opt.value = r.message.lists[i].id;
                    opt.innerHTML = r.message.lists[i].name;
                    select.appendChild(opt);
                }
            } 
        }
    }); 
}

function get_mailchimp_members(page, list_id) {
    frappe.call({
        method: 'mailchimpconnector.mailchimpconnector.page.sync_mailchimp.sync_mailchimp.get_members',
        args: { 'list_id': list_id },
        callback: function(r) {
            if (r.message) {
                var parent = page.main.find(".insert-log-messages").empty();
                for (var i = 0; i < r.message.members.length; i++) {
                    $('<p>' + __(r.message.members[i].email_address) + '</p>').appendTo(parent);
                }
            } 
        }
    });
}

function sync_contacts(frm, list_id) {
	frappe.call({
        method: 'mailchimpconnector.mailchimpconnector.page.sync_mailchimp.sync_mailchimp.sync_contacts',
        args: { 'list_id': list_id },
        callback: function(r) {
            if (r.message) {
                var parent = page.main.find(".insert-log-messages").empty();
                for (var i = 0; i < r.message.members.length; i++) {
                    $('<p>' + __(r.message.members[i].email_address) + '</p>').appendTo(parent);
                }
            } 
        }
    });
}

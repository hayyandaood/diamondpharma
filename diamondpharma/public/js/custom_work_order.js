// Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
frappe.ui.form.off('Work Order', 'show_progress_for_items');
frappe.ui.form.off('Work Order', 'show_progress_for_operations');
frappe.ui.form.on("Work Order", {
	setup: function (frm) {
		frm.set_query("batch_no", function () {
			return {
				filters: [
					["Batch", "item", "=", frm.doc.production_item]
				]
			};
		});
		frappe.db.get_value('Item', frm.doc.production_item, 'create_new_batch')
			.then(r => {
				//console.log(r.message.status) // Open
				if (frm.doc.status in ["Not Saved", "Draft"])
					frm.set_value('automatically_create_new_batch', r.message.create_new_batch);
			});


	},
	refresh: function (frm) {





		frappe.db.get_value('Item', frm.doc.production_item, 'create_new_batch')
			.then(r => {
				//console.log(r.message.status) // Open
				if (frm.doc.status in ["Not Saved", "Draft"])
					frm.set_value('automatically_create_new_batch', r.message.create_new_batch);
			});

		///////////////////////////////////////////////////////////

		//https://discuss.erpnext.com/t/how-to-run-a-custom-script-in-quick-entry/39122

		/*
		This code overwrites the new_doc function of the link fields. I think that something similar can be done for "every" quickentry,
		probably doing the same that is done here to the frappe.new_doc method, saving the script in the folder public/js and
		including the javascript in the app_include_js hook like this:
		
		app_include_js = ["/assets/APP_NAME/js/JS_NAME.js"]
		
		And in the js file, something like:
		
		frappe.old_doc = frappe.new_doc
		
		frappe.new_doc = function(doctype, opts, init_callback) {
			if(doctype == "customdoctype"){
				frappe.old_doc("CUSTOMDOCTYPE", opts, function(dialog) {
					// ETC ETC
				})
			}
		}
		
		Anyways here is the link new_doc overwrite
		
		*/

		//debugger;
		if (!frappe.ui.form.ControlLink.prototype.old_doc) {
			frappe.ui.form.ControlLink.prototype.old_doc = frappe.ui.form.ControlLink.prototype.new_doc;
		}

		frappe.ui.form.ControlLink.prototype.new_doc = function () {

			//if(this.doctype == "DOCTYPE_WITH_LINK_FIELD"){
			if (this.doctype == "Work Order") {
				frappe.ui.form.QuickEntryForm.prototype.old_is_quick = frappe.ui.form.QuickEntryForm.prototype.is_quick_entry;

				// Force quick entry
				frappe.ui.form.QuickEntryForm.prototype.is_quick_entry = function () {
					return true;
				}

				me = this
				var auto_complete = { "item": frm.doc.production_item /*me.get_value()*/ }; // The values are going to be setted in the quick entry
				frappe.new_doc("Batch", auto_complete, function (dialog) {
					// If you don't do this, after the quick entry is saved, the complete form is opened
					frappe.quick_entry.after_insert = function (doc) { /*Do somethin*/ return }

					/*
					SCRIPT FOR THE QUICK ENTRY
					You can use dialog as the quick entry
					with it you can use get_field and jQuery things.
		
					For example:
		
					dialog.get_field("custom_field").$input.on("change", function(e){
						// LOGIC LOGIC LOGIC
					});
		
					You can use set_query too. Example:
		
					dialog.get_field("custom_field").get_query = function(doc,cdt,cdn) {
						return {
							filters:[
								// FILETERS...
							]
						}
					}
		
					*/

					frappe.ui.form.QuickEntryForm.prototype.is_quick_entry = frappe.ui.form.QuickEntryForm.prototype.old_is_quick;
				});

			} else {
				this.old_doc();
			}
		}




		///////////////////////////////////////////////////////////

	},
	show_progress_for_items: function (frm) {
		let master_qty = 0;
		var bars = [];
		var message = '';
		var added_min = false;
		if (frm.doc.qty == frm.doc.minimum_qty) {
			master_qty = frm.doc.qty;
		} else {
			master_qty = frm.doc.minimum_qty;
		}
		// produced qty
		var title = __('{0} items produced', [frm.doc.produced_qty]);

		bars.push({
			'title': title,
			'width': (frm.doc.produced_qty / master_qty * 100) + '%',
			'progress_class': 'progress-bar-success'
		});
		if (bars[0].width == '0%') {
			bars[0].width = '0.5%';
			added_min = 0.5;
		}
		message = title;
		// pending qty
		if (!frm.doc.skip_transfer) {
			var pending_complete = frm.doc.material_transferred_for_manufacturing - frm.doc.produced_qty;
			if (pending_complete) {
				var width = ((pending_complete / master_qty * 100) - added_min);
				title = __('{0} items in progress', [pending_complete]);
				bars.push({
					'title': title,
					'width': (width > 100 ? "99.5" : width) + '%',
					'progress_class': 'progress-bar-warning'
				});
				message = message + '. ' + title;
			}
		}
		frm.dashboard.add_progress(__('Status'), bars, message);
	},

	show_progress_for_operations: function (frm) {
		if (frm.doc.operations && frm.doc.operations.length) {

			let progress_class = {
				"Work in Progress": "progress-bar-warning",
				"Completed": "progress-bar-success"
			};
			let master_qty = 0;
			let bars = [];
			let message = '';
			let title = '';
			let status_wise_oprtation_data = {};
			if (frm.doc.qty == frm.doc.minimum_qty) {
				master_qty = frm.doc.qty;
			} else {
				master_qty = frm.doc.minimum_qty;
			}


			let total_completed_qty = master_qty * frm.doc.operations.length;

			frm.doc.operations.forEach(d => {
				if (!status_wise_oprtation_data[d.status]) {
					status_wise_oprtation_data[d.status] = [d.completed_qty, d.operation];
				} else {
					status_wise_oprtation_data[d.status][0] += d.completed_qty;
					status_wise_oprtation_data[d.status][1] += ', ' + d.operation;
				}
			});

			for (let key in status_wise_oprtation_data) {
				title = __("{0} Operations: {1}", [key, status_wise_oprtation_data[key][1].bold()]);
				bars.push({
					'title': title,
					'width': status_wise_oprtation_data[key][0] / total_completed_qty * 100 + '%',
					'progress_class': progress_class[key]
				});

				message += title + '. ';
			}

			frm.dashboard.add_progress(__('Status'), bars, message);
		}
	},



});
frappe.ui.form.on('Batch', {
	setup: (frm) => {

		//console.log("++++ ", frm.doc.reference_name, frm.doc.reference_doctype);

		if (!frm.doc.reference_doctype) {
			frm.doc.reference_doctype = "Work Order";
			console.log("on setup frm.set_value('item', r.production_item);", frm.doc.reference_name, frm.doc.reference_doctype);
			frm.set_value('reference_doctype', "Work Order");
		}


		if (!frm.doc.item) {
			frappe.db.get_value('Work Order', { name: frm.doc.reference_name }, ['production_item'], (r) => {
				frm.set_value('item', r.production_item);
			});
		}



	},

});


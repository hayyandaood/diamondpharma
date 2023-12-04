// Copyright (c) 2022, oaktc and contributors
// For license information, please see license.txt

frappe.ui.form.on('Leftover', {
	setup: function (frm) {
		frm.set_query('item_code', 'items', function (doc, cdt, cdn) {

			//	let item = locals[cdt][cdn];
			let jop_card_doc = frappe.get_doc('Job Card', doc.job_card);
			let item_list = jop_card_doc.items.map(({ item_code }) => item_code);
			let curr_list = doc.items.map(({ item_code }) => item_code);

			//	let item_list1 = jop_card_doc.items.map(({ item_code, uom }) => [item_code, uom]);




			return {
				filters: [
					['item_code', 'in', item_list],
					['item_code', 'not in', curr_list]

				]
			};
		});
	},
	refresh: function (frm) {
		/*
				frappe.call('diamondpharma.diamondpharma.doctype.leftover.leftover.get_Leftover_Usage_Qty', {
					docnameparam: frm.doc.name
				}).then(r => {
		
					frm.doc.used_qty = r.message;
					frm.refresh_field('used_qty');
				});
		
				console.log(frm.fields_dict);
				console.log(frm);
				frm.doc.vused_qty = frm.doc.pused_qty;
				frm.refresh_field('vused_qty');
		*/
	},

});

frappe.ui.form.on('Leftover Component item', {
	item_name: function (doc, cdt, cdn) {

		//	let row = locals[cdt][cdn];
		let c_row = frappe.get_doc(cdt, cdn);

		//var jop_card_doc = frappe.get_doc('Job Card', doc.job_card)
		//	console.log(doc.fields_dict.job_card.value);
		frappe.db.get_doc('Job Card', doc.fields_dict.job_card.value).then(function (r) {
			let jop_card_doc = r.items;
			//	console.log(r.items);
			let item_list = jop_card_doc.map(({ item_code, uom }) => [item_code, uom]);
			//	console.log(item_list);
			for (let d of item_list) {
				//		console.log(d);
				if (d[0] == c_row.item_code) {
					c_row.uom = d[1];
					refresh_field('uom', cdn, "items");
					break;
				}
			};

			//refresh_field("schedule_date", cdn, "items");

		});



		/*
		let jop_card_doc = frappe.get_doc('Job Card', doc.job_card)
		let item_list = jop_card_doc.let item_list = jop_card_doc.items.map(({ item_code, uom }) => [item_code, uom]);
		console.log(item_list);

		c_row.uom = 'Kg';
		//refresh_field("schedule_date", cdn, "items");
		refresh_field('uom', cdn, "items"); items.map(({ item_code, uom }) => [item_code, uom]);
		console.log(item_list);

		console.log('row');
		console.log(row);
		row.uom = 'Kg'
		console.log(row);
		frappe.set_value(cdt, cdn, 'uom', 'Kg');

		//row.uom = 'Kg';*/
	},

});


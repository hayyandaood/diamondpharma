// Copyright (c) 2023, Diamond pharma and contributors
// For license information, please see license.txt

frappe.ui.form.on('Asset Check Tool', {

	refresh: function (frm) {
		frm.trigger("load_assets");
		frm.trigger("set_primary_action");
	},

	asset_category(frm) {
		frm.trigger("load_assets");
	},

	periodic(frm) {
		frm.trigger("load_assets");
	},

	load_assets: function (frm) {

		console.log("in loading assets")

		frappe.call({
			method: "diamondpharma.diamondpharma.doctype.asset_check_tool.asset_check_tool.load_assets",
			args: {
				asset_category: frm.doc.asset_category,
				periodic: frm.doc.periodic,
			}
		}).then((r) => {
			frm.assets = r.message["asset_list"];
			frm.events.show_unchecked_assets(frm, r.message["asset_list"]);
		});
	},

	show_unchecked_assets(frm, unchecked_assets) {

		const $wrapper = frm.get_field("asset_html").$wrapper;
		$wrapper.empty();
		const asset_wrapper = $(`<div class="asset_wrapper">`).appendTo($wrapper);

		frm.asset_multicheck = frappe.ui.form.make_control({
			parent: asset_wrapper,
			df: {
				fieldname: "asset_multicheck",
				fieldtype: "MultiCheck",
				select_all: true,
				columns: 4,
				get_data: () => {
					return unchecked_assets.map((asset) => {
						return {
							label: `${asset.asset} : ${asset.asset_name}`,
							value: asset.asset,
							checked: 0,
						};
					});
				},
			},
			render_input: true,
		});

		frm.asset_multicheck.refresh_input();
	},


	set_primary_action(frm) {
		frm.disable_save();
		frm.page.set_primary_action(__("Mark Assets Checks"), () => {
			if (frm.assets.length === 0) {
				frappe.msgprint({
					message: __("No assets selected"),
					title: __("Assets Marked"),
					indicator: "green"
				});
				return;
			}

			if (frm.asset_multicheck.get_checked_options().length === 0) {
				frappe.throw({
					message: __("Please select the assets you want to mark."),
					title: __("Mandatory")
				});
			}
			frm.trigger("check_asset");
		});
	},

	check_asset(frm) {
		const marked_assets = frm.asset_multicheck.get_checked_options();

		frappe.call({
			method: "diamondpharma.diamondpharma.doctype.asset_check_tool.asset_check_tool.mark_assets",
			args: {
				asset_list: marked_assets,
				asset_category: frm.doc.asset_category,
				periodic: frm.doc.periodic,
				date: frm.doc.date_checked
			},
			freeze: true,
			freeze_message: __("Checking Assets")
		}).then((r) => {
			if (!r.exc) {
				frappe.show_alert({ message: __("Assets marked successfully"), indicator: "green" });
				frm.refresh();
			}
		});
	},





});

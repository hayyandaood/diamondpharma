// Copyright (c) 2022, oaktc and contributors
// For license information, please see license.txt
frappe.ui.form.on('Attendance Register', {
	refresh: function (frm) {
		frm.add_custom_button(__('Show Absent Employees'), function () {
			frm.trigger("show_absent_employees");
		});
		if (frm.doc.docstatus === 0) {
			frm.add_custom_button(__("Get Active Employees"), () => {
				frappe.confirm(__("This action will delete absenct records. It cannot be undone. Are you certain ?"), function () {
					frm.trigger("get_active_employees");
				});
			});


			let departments = "";
			frappe.db.get_list('Department', {
				filters: {
					disabled: 0,
					parent_department: ["!=", ""],
				},
				fields: ['name'],
				order_by: "name",
				limit: 500,
			}).then(res => {
				res.forEach((element) => {
					departments += "\n" + element.name;
				});
				frm.set_df_property('department', 'options', departments);
				frm.refresh_field('department');
			});

		};

		//	frm.add_custom_button(__('Register Present Employees'), function () {
		//		frm.trigger("register_present_employees");
		//	});
		//	frm.add_custom_button(__('test'), function () {
		//		frm.trigger("test");
		//	});
		if (frm.is_new()) { frm.trigger("get_active_employees"); }

	},
	test: function (frm) {

		//	const table_fields = [
		//		{
		//			fieldname: "mode_of_payment", fieldtype: "Link",
		//			in_list_view: 1, label: "Mode of Payment",
		//			options: "Mode of Payment", reqd: 1
		//		},
		//		{
		//			fieldname: "opening_amount", fieldtype: "Currency",
		//			in_list_view: 1, label: "Opening Amount",
		//			options: "company:company_currency",
		//			change: function () {
		//				dialog.fields_dict.balance_details.df.data.some(d => {
		//					if (d.idx == this.doc.idx) {
		//						d.opening_amount = this.value;
		//						dialog.fields_dict.balance_details.grid.refresh();
		//						return true;
		//					}
		//				});
		//			}
		//		}
		//	];
		var show_dialog = frm.doc.attendance_sheet.filter(d => d.department);
		if (show_dialog && show_dialog.length) {
			//data = [];
			const table_fields = [
				{
					fieldname: "employee",
					fieldtype: "Link",
					in_list_view: 1,
					label: "Employee",
					options: "Employee",
					read_only: 1,
					width: "1"
				},
				{
					default: "Present",
					fieldname: "attendance_status",
					fieldtype: "Select",
					in_list_view: 1,
					label: "Status",
					options: "Present\nAbsent"
				},
				{
					default: "0",
					fieldname: "attendance_check",
					fieldtype: "Check",
					in_list_view: 1,
					label: "Check"
				},
				{
					fetch_from: "employee.employee_name",
					fieldname: "full_name",
					fieldtype: "Data",
					in_list_view: 1,
					label: "Full Name",
					read_only: 1
				},
				{
					fieldname: "department",
					fieldtype: "Data",
					in_list_view: 1,
					in_standard_filter: 1,
					label: "Department",
					read_only: 1,
					search_index: 1

				},
				//{ page_length: 20 },
			];
			var data = frm.doc.attendance_sheet;

			let d = new frappe.ui.Dialog({
				title: 'Attendance Sheet',
				fields: [
					{
						fieldname: "department",
						fieldtype: "Link",
						in_standard_filter: 1,
						label: "Department",
						oldfieldname: "department",
						oldfieldtype: "Link",
						options: "Department",
						change: function () {
							//	this.attendance_sheet.clear()
							//	d.fields_dict.attendance_sheet.grid.data.clear();

							//	d.fields_dict.attendance_sheet.df.data.filter(row => row.department = d.department);
							console.log(data);
							data = [];
							console.log(data);
							console.log(d);
							console.log(d.fields[4].data);
							console.log(d.frm);
							console.log(d.attendance_sheet);
							d.fields_dict.attendance_sheet.grid.refresh();

							//d.attendance_sheet.refresh(data);
							d.refresh_field(d.fields_dict.attendance_sheet);
							console.log(d);
							//var field = d.get_field("attendance_sheet");
							//field.df.read_only = 1;
							//field.df.reqd = true;
							//	field.clear();
							//console.log("field ", field);
							//field.refresh();
							//d.clear();
							//d.fields_dict.attendance_sheet.grid.refresh();
							//d.fields_dict.attendance_sheet.grid.refresh();
							//console.log(d);
						}
					},
					{
						fieldname: "column_break_31",
						fieldtype: "Column Break"
					},
					{
						fieldname: "full_name",
						fieldtype: "Data",
						in_list_view: 1,
						label: "Full Name"
					},
					{
						fieldname: "basic_information",
						fieldtype: "Section Break",
						oldfieldtype: "Section Break"
					},
					{
						fieldname: "attendance_sheet",
						fieldtype: "Table",
						label: "Attendance Sheet",
						cannot_add_rows: false,
						//in_place_edit: true,
						reqd: 1,
						cannot_add_rows: true,
						//	data: frm.doc.attendance_sheet,
						data: data,
						in_place_edit: false,
						get_data: () => {
							return this.data;
						},
						fields: table_fields
					}
				],
				primary_action_label: 'Submit',
				primary_action(values) {
					console.log(values);
					d.hide();
				}
			});
			//d.page_length = 10
			//this.data = frm.doc.attendance_sheet;
			//	this.data = d.fields_dict.attendance_sheet.df.data;

			d.show();

		};

	},
	///--------------------------------------------------------------------------///
	register_present_employees: function (frm) {
		new frappe.ui.form.MultiSelectDialog({
			doctype: "Employee",

			target: frm,
			setters: {
				//name: null,
				//	department: "الادارة - DP",
				department: "*",
				employee_name: "",
			},
			add_filters_group: 1,
			//date_field: "transaction_date",
			columns: ["name", "department", "employee_name"],
			get_query() {
				return {
					filters: { status: ['=', "Active"] }
				}
			},
			action(selections) {
				console.log(selections);
			}
		});



	},
	///--------------------------------------------------------------------------///
	get_active_employees: function (frm) {
		// I have used refresh you can use any trigger
		frm.clear_table('Attendance Register Detail');
		frappe.call({
			method: "frappe.client.get_list",
			//		args: {

			args: {
				"doctype": "Employee",
				"filters": { "status": "Active" },
				//	"fieldname": "name"

				fields: ["name", "department", "employee_name"],
				order_by: "department , employee_name",
				limit_page_length: 100000
			},

			//	doctype: "Employee",
			//	filters: {
			//		"status": "Active"
			//	},	  // You can set any filter you want

			//	fields: ["name", "department"] // you can fetch as many fields as you want separated by a comma
			//		},
			callback: function (r) {
				if (r.message) {
					//	r.message.sort(function (a, b) { a.department > b.department });
					//console.log(r.message);
					cur_frm.clear_table("attendance_sheet");
					r.message.forEach(function (element) {
						var c = frm.add_child("attendance_sheet");

						c.department = element.department;
						c.employee = element.name;

						c.full_name = element.employee_name;

						//c.closed = element.closed;
						//	console.log(r.message);
					});



					//	$.each(response.message, function (i, row) {   // row can be anything, it is merely a name
					//		var child_add = cur_frm.add_child("Attendance Register Detail");  // child_add can be anything
					//		child_add.employee = row.name;
					//		//		child_add.child_table_field_b = row.department; // you can add as many fields as you want
					//		console.log(response.message);     // not really necessary just so you can view the message in the console to check for possible errors               
					//	});
					frm.refresh_field("attendance_sheet");
					frm.get_field("attendance_sheet").grid.df.cannot_delete_rows = true;
					//	frm.get_field("attendance_sheet").grid.df.cannot_add_rows = true;
					frm.set_df_property('attendance_sheet', 'cannot_add_rows', true);
				}
			}
		});
	},

	show_absent_employees: function (frm) {

		var d = new frappe.ui.Dialog({
			title: __("Absent employees"),
			fields: [{ fieldtype: "HTML", fieldname: "ht" }]
		});

		var html_data = '';
		var c = 0;
		html_data = `<div><p><id="data1" values="data1" name="check_data[]"> Absent employees at ${frm.doc.register_date} </p></div>`;
		html_data += `<div><p>  </p></div>`;
		$.each(frm.doc.attendance_sheet, function (i, ctr) {

			if (ctr.attendance_status == "Absent") {
				//console.log(ctr);
				c += 1;
				html_data += `<div><p><id="data2" values="data2" >${c} * ${ctr.department}______  ${ctr.full_name}</p></div>`;


			}

		});
		//console.log(frm.doc.attendance_sheet);
		html_data += `<div><p>  </p></div>`;
		html_data += `<div><p><id="data3" values="data3" name="check_data[]"> Total Absent is ${c} out of ${frm.doc.attendance_sheet.length}</p></div>`;

		d.fields_dict.ht.$wrapper.html(html_data);
		d.set_primary_action(__("Close"), function () {
			d.hide();
		});
		d.show();



	},

	check_attendant_employees: function (frm) {


		const table_fields = [
			{
				fieldname: "employee",
				fieldtype: "Link",
				in_list_view: 1,
				label: "Employee",
				options: "Employee",
				read_only: 1,
				width: "1"
			},
			{
				fetch_from: "employee.employee_name",
				fieldname: "full_name",
				fieldtype: "Data",
				in_list_view: 1,
				label: "Full Name",
				read_only: 1
			},
			{
				fieldname: "department",
				fieldtype: "Data",
				in_list_view: 1,
				in_standard_filter: 1,
				label: "Department",
				read_only: 1,
				search_index: 1

			},
			{
				default: "Present",
				fieldname: "attendance_status",
				fieldtype: "Select",
				in_list_view: 0,
				label: "Status",
				options: "Present\nAbsent"
			},
		];

		let attendance_list = $.map(frm.doc.attendance_sheet, function (d) {
			if (d.department == frm.doc.department) {
				if (d.attendance_status == "Apsent") { d.checked = 0 }
				if (d.attendance_status == "Present") { d.checked = 1 }
				return d
			};
		});
		console.log(attendance_list);
		var me = this;
		//console.log(">>>>>>>>>>", attendance_list);
		if (attendance_list.length >= 1) {
			let attendance_list_data = attendance_list;
			//me.show_dialog = 1;
			let title = __('Check Attendant Employees' + ": " + frm.doc.department);
			let fields = [

				{
					fieldname: "basic_information",
					fieldtype: "Section Break",
					oldfieldtype: "Section Break"
				},
				{
					fieldname: "attendance_sheet",
					fieldtype: "Table",
					label: "Attendance Sheet",
					//in_place_edit: false,
					reqd: 1,
					cannot_add_rows: true,
					cannot_delete_rows: true,
					read_onle: true,


					//	data: frm.doc.attendance_sheet,
					data: attendance_list_data,
					in_place_edit: false,
					get_data: () => {
						return me.attendance_list_data;
					},
					fields: table_fields
				}
			];

			let dialog = new frappe.ui.Dialog({
				title: title, fields: fields
			});
			dialog.fields_dict.attendance_sheet.grid.refresh();
			//	console.log(">>>>>>>>>>>>>>>", dialog.get_field('attendance_sheet'));
			//	console.log(dialog.get_field("attendance_sheet").grid.data.length);
			for (let i = 0; i < dialog.get_field("attendance_sheet").grid.data.length; i++) {
				let row = dialog.fields_dict.attendance_sheet.grid.grid_rows[i];
				//		console.log(row);
				if (row.doc.attendance_status == "Present") {
					row.select(true);
					row.refresh_check();
				}
			}

			dialog.$wrapper.find('.modal-dialog').css("max-width", "90%");
			dialog.$wrapper.find('.modal-dialog').css("width", "90%");


			//	dialog.get_field('attendance_sheet').check_all_rows();
			dialog.show();
			dialog.set_primary_action(__('Transfer'), function () {

				let values = dialog.get_values();
				console.log(values);
				for (let j = 0; j < values.attendance_sheet.length; j++) {
					console.log(values.attendance_sheet[j]);
					console.log(values.attendance_sheet[j].checked);
					if (values.attendance_sheet[j].__checked) {
						console.log("checked");
						frm.doc.attendance_sheet.find(d => d.employee === values.attendance_sheet[j].employee).attendance_status = "Present";
						//frm.doc.attendance_sheet.find(d => d.employee === values.attendance_sheet[j].employee).select(true);
						frm.doc.attendance_sheet.find(d => d.employee === values.attendance_sheet[j].employee).__checked = 1;
						frm.refresh_field("attendance_sheet");
					}
					else {
						console.log("unchecked");
						frm.doc.attendance_sheet.find(d => d.employee === values.attendance_sheet[j].employee).attendance_status = "Absent";
						//frm.doc.attendance_sheet.find(d => d.employee === values.attendance_sheet[j].employee).select(false);
						frm.doc.attendance_sheet.find(d => d.employee === values.attendance_sheet[j].employee).__checked = 0;
						frm.refresh_field("attendance_sheet");
					}

					console.log(frm.doc.attendance_sheet.find(d => d.employee === values.attendance_sheet[j].employee));

				};
				console.log(frm.doc.attendance_sheet);
				//frm.refresh_field("attendance_sheet");
				dialog.hide();

			});
		};

	},


});

frappe.ui.form.on('Attendance Register Detail', {

	attendance_status: function (frm, cdt, cdn) {

		//var d = locals[cdt][cdn];
		let d = frappe.model.get_doc(cdt, cdn);
		//console.log(d);
		if (d.attendance_status == "Present") {
			d.checked = 1;
		};
		if (d.attendance_status == "Absent") {
			d.checked = 0;
		}

		frm.refresh_field("attendance_sheet");

	},

});

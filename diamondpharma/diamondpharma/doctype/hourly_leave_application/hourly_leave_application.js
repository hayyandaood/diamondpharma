// Copyright (c) 2023, oaktc and contributors
// For license information, please see license.txt

cur_frm.add_fetch('employee', 'employee_name', 'employee_name');
cur_frm.add_fetch('employee', 'company', 'company');

frappe.ui.form.on('Hourly Leave Application', {
	setup: function (frm) {
		frm.set_query("leave_approver", function () {
			return {
				query: "erpnext.hr.doctype.department_approver.department_approver.get_approvers",
				filters: {
					employee: frm.doc.employee,
					doctype: "Leave Application"
				}
			};
		});

		frm.set_query("employee", erpnext.queries.employee);
	},
	onload: function (frm) {
		// Ignore cancellation of doctype on cancel all.
		frm.ignore_doctypes_on_cancel_all = ["Leave Ledger Entry"];

		if (!frm.doc.posting_date) {
			frm.set_value("posting_date", frappe.datetime.get_today());
		}
		if (frm.doc.docstatus == 0) {
			return frappe.call({
				method: "erpnext.hr.doctype.leave_application.leave_application.get_mandatory_approval",
				args: {
					doctype: frm.doc.doctype,
				},
				callback: function (r) {
					if (!r.exc && r.message) {
						frm.toggle_reqd("leave_approver", true);
					}
				}
			});
		}
	},
	make_dashboard: function (frm) {
		var leave_details;
		let lwps;
		if (frm.doc.employee) {
			frappe.call({
				method: "erpnext.hr.doctype.leave_application.leave_application.get_leave_details",
				async: false,
				args: {
					employee: frm.doc.employee,
					date: frm.doc.from_date || frm.doc.posting_date
				},
				callback: function (r) {
					if (!r.exc && r.message['leave_allocation']) {
						leave_details = r.message['leave_allocation'];
					}
					if (!r.exc && r.message['leave_approver']) {
						frm.set_value('leave_approver', r.message['leave_approver']);
					}
					lwps = r.message["lwps"];
				}
			});
			$("div").remove(".form-dashboard-section.custom");
			frm.dashboard.add_section(
				frappe.render_template('leave_application_dashboard', {
					data: leave_details
				}),
				__("Allocated Leaves")
			);
			frm.dashboard.show();
			let allowed_leave_types = Object.keys(leave_details);

			// lwps should be allowed, lwps don't have any allocation
			allowed_leave_types = allowed_leave_types.concat(lwps);

			frm.set_query('leave_type', function () {
				return {
					filters: [
						['leave_type_name', 'in', allowed_leave_types]
					]
				};
			});
		}
	},
	refresh: function (frm) {
		cur_frm.set_intro("");
		if (frm.doc.__islocal && !in_list(frappe.user_roles, "Employee")) {
			frm.set_intro(__("Fill the form and save it"));
		}

		if (!frm.doc.employee && frappe.defaults.get_user_permissions()) {
			const perm = frappe.defaults.get_user_permissions();
			if (perm && perm['Employee']) {
				frm.set_value('employee', perm['Employee'].map(perm_doc => perm_doc.doc)[0]);
			}
		}
	},
	employee: function (frm) {
		console.log("frappe.db.get_single_value('HR Settings', 'standard_working_hours')");
		frm.trigger("make_dashboard");
		frm.trigger("get_leave_balance");
		frm.trigger("set_leave_approver");
		frappe.db.get_single_value('HR Settings', 'standard_working_hours').then(val => {
			if (val) {
				console.log(val);
				frm.set_value("standard_working_hours", val);
				refresh_field('standard_working_hours');
			}

			//frm.doc.standard_working_hours = val;
		});



	},

	leave_approver: function (frm) {
		if (frm.doc.leave_approver) {
			frm.set_value("leave_approver_name", frappe.user.full_name(frm.doc.leave_approver));
		}
	},

	leave_type: function (frm) {
		frm.trigger("get_leave_balance");
	},

	set_leave_approver: function (frm) {
		if (frm.doc.employee) {
			// server call is done to include holidays in leave days calculations
			return frappe.call({
				method: 'erpnext.hr.doctype.leave_application.leave_application.get_leave_approver',
				args: {
					"employee": frm.doc.employee,
				},
				callback: function (r) {
					if (r && r.message) {
						frm.set_value('leave_approver', r.message);
					}
				}
			});
		}
	},
	get_leave_balance: function (frm) {
		if (frm.doc.docstatus === 0 && frm.doc.employee && frm.doc.leave_type && frm.doc.hourly_leave_date) {
			return frappe.call({
				method: "erpnext.hr.doctype.leave_application.leave_application.get_leave_balance_on",
				args: {
					employee: frm.doc.employee,
					date: frm.doc.hourly_leave_date,
					to_date: frm.doc.hourly_leave_date,
					leave_type: frm.doc.leave_type,
					consider_all_leaves_in_the_allocation_period: 1
				},
				callback: function (r) {
					if (!r.exc && r.message) {
						frm.set_value('leave_balance', r.message);
					} else {
						frm.set_value('leave_balance', "0");
					}
				}
			});
		}
	},


	from_time: function (frm) {
		calculateToTime(frm);
	},
	leave_duration: function (frm) {
		calculateToTime(frm);
		//frm.doc.post_to_balance_duration = 0;
		//frm.doc.remaining_not_posted_duration = 0;
		console.log(frm.doc.post_to_balance_duration, '*****', frm.doc.remaining_not_posted_duration);

		console.log(frm.doc.employee, moment(frm.doc.hourly_leave_date).year(),);

		// Call the Python function using a server call
		frappe.call({
			method: "diamondpharma.diamondpharma.doctype.hourly_leave_application.hourly_leave_application.get_latest_hourly_leave_application",
			args: {
				employee: frm.doc.employee,
				//year: moment(frm.doc.hourly_leave_date).year()
				hourly_leave_date: frm.doc.hourly_leave_date
			},
			callback: function (response) {
				// Set the latest hourly leave application in the form
				const latest_leave_application = response.message;
				console.log(frm.doc.hourly_leave_date, "responce= ", response);
				if (latest_leave_application) {
					if (!frm.doc.hourly_leave_exception) {


						console.log(latest_leave_application);
						frm.set_value("post_to_balance_duration", latest_leave_application.post_to_balance_duration);
						frm.set_value("remaining_not_posted_duration", latest_leave_application.remaining_not_posted_duration + frm.doc.leave_duration);
						console.log(frm.doc.post_to_balance_duration, '**1***', frm.doc.remaining_not_posted_duration);
					}
					else {
						console.log("frm.doc.hourly_leave_exception: ", frm.doc.hourly_leave_exception);
						frm.set_value("post_to_balance_duration", latest_leave_application.post_to_balance_duration);
						frm.set_value("remaining_not_posted_duration", latest_leave_application.remaining_not_posted_duration);

					}
				} else {
					console.log("/////////////////", `frm.set_value("post_to_balance_duration", 0);`);
					frm.set_value("post_to_balance_duration", 0);
					frm.set_value("remaining_not_posted_duration", frm.doc.leave_duration);
					console.log(frm.doc.post_to_balance_duration, '**2***', frm.doc.remaining_not_posted_duration);
				}
			}
		});




		//		updateRemainingDuration(frm);
	},
	validate: function (frm) {

		if (frm.doc.standard_working_hours == 0) {
			frappe.db.get_single_value('HR Settings', 'standard_working_hours').then(val => {
				if (val) {
					frm.set_value("standard_working_hours", val);
					frm.save();
				}

				//frm.doc.standard_working_hours = val;
			});
		}

		// Code to execute when the form is validated
		// e.g. validating form fields or displaying an error message if a required field is empty
		// Check if leave_duration is less than 8 hours
		var duration = frm.doc.leave_duration;
		console.log(duration, "  ", frm.doc.leave_duration);
		if (duration >= (frm.doc.standard_working_hours * 60 * 60)) {
			frappe.msgprint(__('Leave duration cannot be more than or equal ' + frm.doc.standard_working_hours + ' hours'));
			validated = false;
		};
	},

	//	before_submit: function (frm) {
	// Code to execute before the form is submitted
	// e.g. confirming with the user before submitting the form or updating a related field before submission

	// reset values to zero at the beginning of a new year
	//		var year = moment(frm.doc.from_time).year();
	//		var last_year = moment().subtract(1, 'year').year();
	//		if (year !== last_year && frm.doc.docstatus === 0) {
	//			frm.set_value('post_to_balance_duration', 0);
	//			frm.set_value('remaining_not_posted_duration', 0);
	//		}
	//	},

	on_submit: function (frm) {
		// Code to execute after the form is successfully submitted
		// e.g. sending an email notification to a specific user or updating a related field after submission
		//	var duration = frm.doc.leave_duration;
		//	if (duration < frm.doc.standard_working_hours * 60 * 60) {
		//		frm.set_value('post_to_balance_duration', 0);
		//		frm.set_value('remaining_not_posted_duration', duration);
		//	}
	},

	on_cancel: function (frm) {
		// Code to execute when the form is cancelled
		// e.g. resetting form fields or updating a related field after cancellation
	},
});

function calculateToTime(frm) {
	var from_time = frm.doc.from_time;
	var leave_duration = frm.doc.leave_duration;
	if (from_time && leave_duration) {
		var moment_from_time = moment(from_time, 'HH:mm:ss');
		var moment_leave_duration = moment.duration(parseInt(leave_duration), 'seconds');
		var moment_to_time = moment_from_time.clone().add(moment_leave_duration).format('HH:mm:ss');
		frm.set_value('to_time', moment_to_time);
	}
};
//function updateRemainingDuration(frm) {
//	let leave_duration = frm.doc.leave_duration;
//	let remaining_duration = frm.doc.remaining_not_posted_duration;
//	console.log(leave_duration, '---------', frm.doc);
//	if (leave_duration && remaining_duration) {
//		let moment_remaining_duration = moment.duration(parseInt(remaining_duration), 'seconds');
//		let moment_leave_duration = moment.duration(parseInt(leave_duration), 'seconds');
//		let updated_remaining_duration = moment_remaining_duration.add(moment_leave_duration).asSeconds();
//		frm.set_value('remaining_not_posted_duration', updated_remaining_duration);
//	}
//};


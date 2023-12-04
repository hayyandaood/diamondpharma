from erpnext.hr.doctype.leave_application.leave_application import LeaveApplication
import frappe


class DiamondpharmaLeaveApplication(LeaveApplication):
    def on_submit(self):
        super().on_submit()

        hourly_leave_application_exists = frappe.db.exists(
            "Hourly Leave Application",
            {
                "posted_leave_application": self.name,
            },
        )
        # hourly_leave_applicationroom_doctype = frappe.qb.DocType(
        #    "Hourly Leave Application"
        # )
        # hourly_leave_application_exists = (
        #    frappe.qb.from_(hourly_leave_applicationroom_doctype)
        #    .select("posted_leave_application")
        #    .where(
        #        hourly_leave_applicationroom_doctype.posted_leave_application
        #        == self.name
        #    )
        #    .where(hourly_leave_applicationroom_doctype.docstatus == 1)
        # ).run(as_dict=True)

        if hourly_leave_application_exists:
            hourly_leave_application_exists = frappe.get_doc(
                "Hourly Leave Application", hourly_leave_application_exists
            )
            Leave_days = (
                hourly_leave_application_exists.remaining_not_posted_duration
                // (hourly_leave_application_exists.standard_working_hours * 60 * 60)
            )

            hourly_leave_application_exists.db_set(
                "post_to_balance_duration",
                hourly_leave_application_exists.post_to_balance_duration
                + (
                    Leave_days
                    * (hourly_leave_application_exists.standard_working_hours * 60 * 60)
                ),
            )

            hourly_leave_application_exists.db_set(
                "remaining_not_posted_duration",
                (
                    hourly_leave_application_exists.remaining_not_posted_duration
                    - (
                        Leave_days
                        * (
                            hourly_leave_application_exists.standard_working_hours
                            * 60
                            * 60
                        )
                    )
                ),
            )

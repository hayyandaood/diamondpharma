# Copyright (c) 2023, oaktc and contributors
# For license information, please see license.txt

# import frappe
from datetime import datetime
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.data import add_days, cint, get_datetime
from frappe.utils import get_fullname


class HourlyLeaveApplication(Document):
    def validate(self):
        if self.get("employee") and self.get("hourly_leave_date"):
            self.validate_hourly_leave_application()

    def validate_hourly_leave_application(self):
        # hourly_leave_date = self.hourly_leave_date.strftime("%Y-%m-%d")
        hourly_leave_date = self.hourly_leave_date
        employee = self.employee
        existing_doc = frappe.db.exists(
            "Hourly Leave Application",
            {
                "employee": employee,
                "hourly_leave_date": hourly_leave_date,
                "name": ("!=", self.name) if self.name else "",
                "docstatus": "1",
            },
        )
        if existing_doc:
            if (
                self.get_total_in_date_duration(employee, hourly_leave_date)
                >= self.standard_working_hours
            ):
                frappe.throw(
                    f"Another Hourly Leave Application document exists for {employee} name {self.employee_name} on {hourly_leave_date} and the total duration is more than on day."
                )

    def get_total_in_date_duration(employee, date):
        sum_of_duration = (
            frappe.db.sql(
                """
            SELECT SUM(remaining_not_posted_duration) 
            FROM `tabHourly Leave Application` 
            WHERE employee = %s AND hourly_leave_date < %s AND docstatus = 1
        """,
                (employee, date),
            )[0][0]
            or 0
        )

        return sum_of_duration

    """def before_save(doc, method):
        employee = doc.employee
        date = doc.hourly_leave_date
        remaining_duration = get_remaining_duration(employee, date)
        duration = doc.leave_duration
        total_duration = remaining_duration + duration
        if total_duration >= 28800:  # 8 hours in seconds
            doc.remaining_not_posted_duration = 0
        else:
            doc.remaining_not_posted_duration = 28800 - total_duration  """

    def on_update(self):
        if self.status == "Open" and self.docstatus < 1:
            # notify leave approver about creation
            if frappe.db.get_single_value("HR Settings", "send_leave_notification"):
                self.notify_leave_approver()

        # share_doc_with_approver(self, self.leave_approver)

    def notify_leave_approver(self):
        if self.leave_approver:
            parent_doc = frappe.get_doc("Hourly Leave Application", self.name)
            args = parent_doc.as_dict()

            template = frappe.db.get_single_value(
                "HR Settings", "leave_approval_notification_template"
            )
            if not template:
                frappe.msgprint(
                    _(
                        "Please set default template for Leave Approval Notification in HR Settings."
                    )
                )
                return
            email_template = frappe.get_doc("Email Template", template)
            message = frappe.render_template(email_template.response, args)

            self.notify(
                {
                    # for post in messages
                    "message": message,
                    "message_to": self.leave_approver,
                    # for email
                    "subject": email_template.subject,
                }
            )

    def notify(self, args):
        args = frappe._dict(args)
        # args -> message, message_to, subject
        if cint(self.follow_via_email):
            contact = args.message_to
            if not isinstance(contact, list):
                if not args.notify == "employee":
                    contact = frappe.get_doc("User", contact).email or contact

            sender = dict()
            sender["email"] = frappe.get_doc("User", frappe.session.user).email
            sender["full_name"] = get_fullname(sender["email"])

            try:
                frappe.sendmail(
                    recipients=contact,
                    sender=sender["email"],
                    subject=args.subject,
                    message=args.message,
                )
                frappe.msgprint(_("Email sent to {0}").format(contact))
            except frappe.OutgoingEmailError:
                pass

    def on_submit(self):
        if self.status in ["Open", "Cancelled"]:
            frappe.throw(
                _(
                    "Only Hourly Leave Applications with status 'Approved' and 'Rejected' can be submitted"
                )
            )

        # create Leave Application if remaining_not_posted_duration is more than one day
        if self.remaining_not_posted_duration >= (
            self.standard_working_hours * 60 * 60
        ):
            # how many days are to be Leave Applications
            Leave_days = self.remaining_not_posted_duration // (
                self.standard_working_hours * 60 * 60
            )
            # frappe.throw(("{Leave_days}"))
            if Leave_days > 0:
                # create a new Leave Application
                doc = frappe.new_doc("Leave Application")
                doc.employee = self.employee
                doc.employee_name = self.employee_name
                doc.leave_type = self.leave_type
                doc.department = self.department
                doc.from_date = self.hourly_leave_date
                doc.to_date = add_days(self.hourly_leave_date, Leave_days - 1)
                doc.total_leave_days = Leave_days
                doc.description = (
                    "Converted Hourly Leave/s to Leave/s"
                    + " "
                    + "based on Hourly Leave Application document name: "
                    + self.name
                )
                doc.leave_approver = self.leave_approver
                doc.leave_approver_name = self.leave_approver_name
                doc.status = "Open"
                doc.posting_date = self.posting_date
                doc.company = self.company

                doc.insert()
                # self.db_set(
                #    "remaining_not_posted_duration",
                #    (
                #        self.remaining_not_posted_duration
                #        - (Leave_days * (self.standard_working_hours * 60 * 60))
                #    ),
                # )
                # self.db_set(
                #    "post_to_balance_duration",
                #    self.post_to_balance_duration
                #    + (Leave_days * (self.standard_working_hours * 60 * 60)),
                # )
                self.db_set("posted_leave_application", doc.name)
        # notify leave applier about approval

        if frappe.db.get_single_value("HR Settings", "send_leave_notification"):
            self.notify_employee()

    def notify_employee(self):
        employee = frappe.get_doc("Employee", self.employee)
        if not employee.user_id:
            return

        parent_doc = frappe.get_doc("Hourly Leave Application", self.name)
        args = parent_doc.as_dict()

        template = frappe.db.get_single_value(
            "HR Settings", "leave_status_notification_template"
        )
        if not template:
            frappe.msgprint(
                _(
                    "Please set default template for Leave Status Notification in HR Settings."
                )
            )
            return
        email_template = frappe.get_doc("Email Template", template)
        message = frappe.render_template(email_template.response, args)

        self.notify(
            {
                # for post in messages
                "message": message,
                "message_to": employee.user_id,
                # for email
                "subject": email_template.subject,
                "notify": "employee",
            }
        )


@frappe.whitelist()
def get_remaining_duration(employee, date):
    remaining_duration = (
        frappe.db.sql(
            """
        SELECT SUM(remaining_not_posted_duration) 
        FROM `tabHourly Leave Application` 
        WHERE employee = %s AND hourly_leave_date < %s AND docstatus = 1
    """,
            (employee, date),
        )[0][0]
        or 0
    )

    return remaining_duration


@frappe.whitelist()
def get_latest_hourly_leave_application(employee, hourly_leave_date):

    latest_leave_application = frappe.db.sql(
        """select name,hourly_leave_date,from_time,leave_duration, posting_date,post_to_balance_duration,remaining_not_posted_duration from `tabHourly Leave Application`
			where employee=%s and docstatus=1 and hourly_leave_date <= %s 
			order by hourly_leave_date desc , from_time desc""",
        (employee, hourly_leave_date),
        as_dict=1,
    )

    if latest_leave_application:
        if (
            get_datetime(latest_leave_application[0].hourly_leave_date).year
            == get_datetime(hourly_leave_date).year
        ):
            return latest_leave_application[0]

    return None

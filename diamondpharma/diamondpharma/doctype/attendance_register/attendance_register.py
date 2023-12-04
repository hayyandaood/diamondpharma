# Copyright (c) 2022, oaktc and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class AttendanceRegister(Document):
    def on_submit(self):
        if not self.attendance_sheet:
            frappe.throw(_("Employees cannot be 0"))

        for row in self.attendance_sheet:
            attendance_name = frappe.db.exists(
                "Attendance",
                dict(
                    employee=row.employee,
                    attendance_date=self.register_date,
                    docstatus=("!=", 2),
                ),
            )
            if not attendance_name:
                doc = frappe.new_doc("Attendance")
                doc.employee = row.employee
                doc.employee_name = row.full_name
                doc.attendance_date = self.register_date
                doc.company = self.company
                doc.status = row.attendance_status
                doc.flags.ignore_validate = True
                doc.insert(ignore_permissions=False)
                doc.submit()

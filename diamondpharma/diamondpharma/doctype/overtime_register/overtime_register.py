# Copyright (c) 2022, oaktc and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class OvertimeRegister(Document):
    def on_submit(self):
        if not self.overtime_sheet:
            frappe.throw(_("Employees cannot be 0"))

        for row in self.overtime_sheet:
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
                doc.status = "Present"
                doc.flags.ignore_validate = True
                doc.overtime_duration = row.overtime_duration
                doc.overtime_percentage = row.overtime_percentage
                doc.overtime_type = row.overtime_type
                doc.insert(ignore_permissions=False)
                doc.submit()
            else:
                doc = frappe.get_doc("Attendance", attendance_name)
                doc.db_set("overtime_duration", row.overtime_duration)
                doc.db_set("overtime_percentage", row.overtime_percentage)
                doc.db_set("overtime_type", row.overtime_type)
                # doc.db_update()

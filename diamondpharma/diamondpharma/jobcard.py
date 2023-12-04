from __future__ import unicode_literals
import json
import frappe
from frappe import _
from erpnext.manufacturing.doctype.job_card.job_card import JobCard
from frappe.utils import get_datetime, time_diff_in_seconds


class DiamondpharmaJobCard(JobCard):
    def add_time_log(self, args):
        last_row = []
        employees = args.employees
        if isinstance(employees, str):
            employees = json.loads(employees)

        if self.time_logs and len(self.time_logs) > 0:
            last_row = self.time_logs[-1]

        self.reset_timer_value(args)
        if last_row and args.get("complete_time"):
            time_logs_count = 0
            for zero_qty_row in self.time_logs:
                if zero_qty_row.get("completed_qty") == 0.0:
                    time_logs_count += 1
            # time_logs_count = len(self.time_logs)
            job_card_completed_qty = args.get("completed_qty") or 0.0
            emploee_qty = job_card_completed_qty // time_logs_count
            emploees_total = 0
            for row in self.time_logs:
                if not row.to_time:
                    row.update(
                        {
                            "to_time": get_datetime(args.get("complete_time")),
                            "operation": args.get("sub_operation"),
                            # "completed_qty": args.get("completed_qty") or 0.0,
                            "completed_qty": emploee_qty or 0.0,
                        }
                    )
                    emploees_total += emploee_qty
            if job_card_completed_qty > emploees_total:
                self.time_logs[-1].update(
                    {
                        "completed_qty": (emploee_qty or 0.0)
                        + (job_card_completed_qty - emploees_total)
                    }
                )

        elif args.get("start_time"):
            new_args = frappe._dict(
                {
                    "from_time": get_datetime(args.get("start_time")),
                    "operation": args.get("sub_operation"),
                    "completed_qty": 0.0,
                }
            )

            if employees:
                for name in employees:
                    new_args.employee = name.get("employee")
                    self.add_start_time_log(new_args)
            else:
                self.add_start_time_log(new_args)

        if not self.employee and employees:
            self.set_employees(employees)

        if self.status == "On Hold":
            self.current_time = time_diff_in_seconds(
                last_row.to_time, last_row.from_time
            )

        self.save()

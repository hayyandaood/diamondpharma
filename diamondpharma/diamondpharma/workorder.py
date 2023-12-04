# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _
from erpnext.manufacturing.doctype.work_order.work_order import (
    OverProductionError,
    StockOverProductionError,
    WorkOrder,
)
from frappe.utils import (
    flt,
)


class DiamondpharmaWorkOrder(WorkOrder):
    def get_status(self, status=None):
        """Return the status based on stock entries against this work order"""
        if not status:
            status = self.status

        if self.docstatus == 0:
            status = "Draft"
        elif self.docstatus == 1:
            if status != "Stopped":
                stock_entries = frappe._dict(
                    frappe.db.sql(
                        """select purpose, sum(fg_completed_qty)
					from `tabStock Entry` where work_order=%s and docstatus=1
					group by purpose""",
                        self.name,
                    )
                )

                status = "Not Started"
                if stock_entries:
                    status = "In Process"
                    produced_qty = stock_entries.get("Manufacture")

                    if flt(self.qty) == flt(self.minimum_qty):
                        if flt(produced_qty) >= flt(self.qty):
                            status = "Completed"
                    else:
                        if flt(produced_qty) >= flt(self.minimum_qty):
                            status = "Completed"

        else:
            status = "Cancelled"

        return status

    def update_work_order_qty(self):
        """Update **Manufactured Qty** and **Material Transferred for Qty** in Work Order
        based on Stock Entry"""

        allowance_percentage = flt(
            frappe.db.get_single_value(
                "Manufacturing Settings", "overproduction_percentage_for_work_order"
            )
        )

        for purpose, fieldname in (
            ("Manufacture", "produced_qty"),
            (
                "Material Transfer for Manufacture",
                "material_transferred_for_manufacturing",
            ),
        ):
            if (
                purpose == "Material Transfer for Manufacture"
                and self.operations
                and self.transfer_material_against == "Job Card"
            ):
                continue

            qty = flt(
                frappe.db.sql(
                    """select sum(fg_completed_qty)
				from `tabStock Entry` where work_order=%s and docstatus=1
				and purpose=%s""",
                    (self.name, purpose),
                )[0][0]
            )

            if flt(self.qty) == flt(self.minimum_qty):
                completed_qty = self.qty + (allowance_percentage / 100 * self.qty)
                if qty > completed_qty:
                    frappe.throw(
                        _(
                            "{0} ({1}) cannot be greater than planned quantity ({2}) in Work Order {3}"
                        ).format(
                            self.meta.get_label(fieldname),
                            qty,
                            completed_qty,
                            self.name,
                        ),
                        StockOverProductionError,
                    )
            else:
                completed_qty = (
                    self.qty
                    + (allowance_percentage / 100 * self.qty)
                    - (self.qty - flt(self.minimum_qty))
                )
                """
                if qty < completed_qty:
                    frappe.throw(
                        _(
                            "{0} ({1}) cannot be lesser than planned quantity ({2}) in Work Order {3}"
                        ).format(
                            self.meta.get_label(fieldname),
                            qty,
                            completed_qty,
                            self.name,
                        ),
                        StockOverProductionError,
                    )
"""
            self.db_set(fieldname, qty)
            self.set_process_loss_qty()

            from erpnext.selling.doctype.sales_order.sales_order import (
                update_produced_qty_in_so_item,
            )

            if self.sales_order and self.sales_order_item:
                update_produced_qty_in_so_item(self.sales_order, self.sales_order_item)

        if self.production_plan:
            self.update_production_plan_status()

    def update_operation_status(self):
        allowance_percentage = flt(
            frappe.db.get_single_value(
                "Manufacturing Settings", "overproduction_percentage_for_work_order"
            )
        )
        max_allowed_qty_for_wo = flt(self.qty) + (
            allowance_percentage / 100 * flt(self.qty)
        )

        if flt(self.qty) == flt(self.minimum_qty):
            for d in self.get("operations"):
                if not d.completed_qty:
                    d.status = "Pending"
                elif flt(d.completed_qty) < flt(self.qty):
                    d.status = "Work in Progress"
                elif flt(d.completed_qty) == flt(self.qty):
                    d.status = "Completed"
                elif flt(d.completed_qty) <= max_allowed_qty_for_wo:
                    d.status = "Completed"
                else:
                    frappe.throw(
                        _("Completed Qty cannot be greater than 'Qty to Manufacture'")
                    )
        else:
            for d in self.get("operations"):
                if not d.completed_qty:
                    d.status = "Pending"
                elif flt(d.completed_qty) < flt(self.minimum_qty):
                    d.status = "Work in Progress"
                elif flt(d.completed_qty) == flt(self.minimum_qty):
                    d.status = "Completed"
                elif flt(d.completed_qty) <= max_allowed_qty_for_wo:
                    d.status = "Completed"
                else:
                    frappe.throw(
                        _("Completed Qty cannot be greater than 'Qty to Manufacture'")
                    )

    def validate_qty(self):
        if flt(self.qty) == flt(self.minimum_qty):
            if not self.qty > 0:
                frappe.throw(_("Quantity to Manufacture must be greater than 0."))

            if (
                self.production_plan
                and self.production_plan_item
                and not self.production_plan_sub_assembly_item
            ):
                qty_dict = frappe.db.get_value(
                    "Production Plan Item",
                    self.production_plan_item,
                    ["planned_qty", "ordered_qty"],
                    as_dict=1,
                )

                if not qty_dict:
                    return

                allowance_qty = (
                    flt(
                        frappe.db.get_single_value(
                            "Manufacturing Settings",
                            "overproduction_percentage_for_work_order",
                        )
                    )
                    / 100
                    * qty_dict.get("planned_qty", 0)
                )

                max_qty = (
                    qty_dict.get("planned_qty", 0)
                    + allowance_qty
                    - qty_dict.get("ordered_qty", 0)
                )

                if not max_qty > 0:
                    frappe.throw(
                        _("Cannot produce more item for {0}").format(
                            self.production_item
                        ),
                        OverProductionError,
                    )
                elif self.qty > max_qty:
                    frappe.throw(
                        _("Cannot produce more than {0} items for {1}").format(
                            max_qty, self.production_item
                        ),
                        OverProductionError,
                    )
        else:
            if not self.qty > 0:
                frappe.throw(_("Quantity to Manufacture must be greater than 0."))

            if (
                self.production_plan
                and self.production_plan_item
                and not self.production_plan_sub_assembly_item
            ):
                qty_dict = frappe.db.get_value(
                    "Production Plan Item",
                    self.production_plan_item,
                    ["planned_qty", "ordered_qty"],
                    as_dict=1,
                )

                if not qty_dict:
                    return

                allowance_qty = (
                    flt(
                        frappe.db.get_single_value(
                            "Manufacturing Settings",
                            "overproduction_percentage_for_work_order",
                        )
                    )
                    / 100
                    * qty_dict.get("planned_qty", 0)
                )

                max_qty = (
                    qty_dict.get("planned_qty", 0)
                    + allowance_qty
                    - qty_dict.get("ordered_qty", 0)
                )

                if not max_qty > 0:
                    frappe.throw(
                        _("Cannot produce more item for {0}").format(
                            self.production_item
                        ),
                        OverProductionError,
                    )
                elif self.minimum_qty > max_qty:
                    frappe.throw(
                        _("Cannot produce more than {0} items for {1}").format(
                            max_qty, self.production_item
                        ),
                        OverProductionError,
                    )

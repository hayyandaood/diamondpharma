# Copyright (c) 2022, oaktc and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from frappe.utils.data import flt


class Leftover(Document):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.used_qty = self.set_used_qty()
        self.remaining_quantity_for_use = flt(self.qty) - flt(self.used_qty)

    def set_used_qty(self):
        values = flt(
            frappe.db.sql(
                """
            select sum(lou.qty) 
            from `tabLeftover Usage` lou 
            where lou.leftover = %s 
            """,
                (self.name),
            )[0][0]
        )
        return flt(values if values else 0)


@frappe.whitelist()
def get_Leftover_Usage_Qty(docnameparam):
    values = flt(
        frappe.db.sql(
            """
            select sum(lou.qty) 
            from `tabLeftover Usage` lou 
            where lou.leftover = %s 
        """,
            (docnameparam),
        )[0][0]
    )

    val = flt(values if values else 0)
    return val


@frappe.whitelist()
def get_Leftover_Items(docnameparam, qty_percent):
    items_rows = frappe._dict()
    if flt(qty_percent) > 0:
        items_rows = frappe.db.sql(
            """
            select item_code,item_name,qty,uom
            from `tabLeftover Component item` 
            where parent = %s 
            and
            parenttype = "Leftover"
            and
            docstatus = 1
            and
            parentfield = "items"
        """,
            (docnameparam),
            as_dict=True,
        )

        for d in items_rows:
            d.new_qty = (flt(d.qty) * flt(qty_percent)) / 100

    if items_rows:
        return items_rows
    else:
        return []

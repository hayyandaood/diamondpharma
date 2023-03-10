from __future__ import unicode_literals
from typing_extensions import Self
import frappe
from frappe import _
from erpnext.manufacturing.doctype.work_order.work_order import (
    add_variant_item,
    get_item_details,
)

from frappe.utils import ceil, cstr, flt


@frappe.whitelist()
def make_work_order(bom_no, item, qty=0, project=None, variant_items=None):
    if not frappe.has_permission("Work Order", "write"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    item_details = get_item_details(item, project)

    wo_doc = frappe.new_doc("Work Order")
    wo_doc.production_item = item
    wo_doc.update(item_details)
    wo_doc.bom_no = bom_no

    if flt(qty) > 0:
        wo_doc.qty = flt(qty)
        wo_doc.get_items_and_operations_from_bom()
        min_allowed_percentage = flt(
            frappe.db.get_single_value(
                "Manufacturing Custom Settings", "under_production_percent_allowance"
            )
        )
        if min_allowed_percentage == 0:
            wo_doc.minimum_qty = flt(qty)
        else:
            uom = frappe.get_value("Item", item, "stock_uom")
            must_be_whole_number =from __future__ import unicode_literals
from typing_extensions import Self
import frappe
from frappe import _
from erpnext.manufacturing.doctype.work_order.work_order import (
    add_variant_item,
    get_item_details,
)

from frappe.utils import ceil, cstr, flt


@frappe.whitelist()
def make_work_order(bom_no, item, qty=0, project=None, variant_items=None):
    if not frappe.has_permission("Work Order", "write"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    item_details = get_item_details(item, project)

    wo_doc = frappe.new_doc("Work Order")
    wo_doc.production_item = item
    wo_doc.update(item_details)
    wo_doc.bom_no = bom_no

    if flt(qty) > 0:
        wo_doc.qty = flt(qty)
        wo_doc.get_items_and_operations_from_bom()
        min_allowed_percentage = flt(
            frappe.db.get_single_value(
                "Manufacturing Custom Settings", "under_production_percent_allowance"
            )
        )
        if min_allowed_percentage == 0:
            wo_doc.minimum_qty = flt(qty)
        else:
            uom = frappe.get_value("Item", item, "stock_uom")
            must_be_whole_number = frappe.db.get_value(
                "UOM", uom, "must_be_whole_number", cache=True
            )

            if must_be_whole_number:
                wo_doc.minimum_qty = flt(
                    ceil(flt(flt(qty) - (min_allowed_percentage / 100 * flt(qty))))
                )
            else:
                wo_doc.minimum_qty = flt(
                    flt(qty) - (min_allowed_percentage / 100 * flt(qty))
                )

    if variant_items:
        add_variant_item(variant_items, wo_doc, bom_no, "required_items")

    return wo_doc


# @frappe.whitelist()
# def make_stock_entry(work_order_id, purpose, qty=None):
#     work_order = frappe.get_doc("Work Order", work_order_id)
#     if not frappe.db.get_value("Warehouse", work_order.wip_warehouse, "is_group"):
#         wip_warehouse = work_order.wip_warehouse
#     else:
#         wip_warehouse = None

#     stock_entry = frappe.new_doc("Stock Entry")
#     stock_entry.purpose = purpose
#     stock_entry.work_order = work_order_id
#     stock_entry.company = work_order.company
#     stock_entry.from_bom = 1
#     stock_entry.bom_no = work_order.bom_no
#     stock_entry.use_multi_level_bom = work_order.use_multi_level_bom
#     # accept 0 qty as well
#     stock_entry.fg_completed_qty = (
#         qty if qty is not None else (flt(work_order.qty) - flt(work_order.produced_qty))
#     )

#     if work_order.bom_no:
#         stock_entry.inspection_required = frappe.db.get_value(
#             "BOM", work_order.bom_no, "inspection_required"
#         )

#     if purpose == "Material Transfer for Manufacture":
#         stock_entry.to_warehouse = wip_warehouse
#         stock_entry.project = work_order.project
#     else:
#         stock_entry.from_warehouse = wip_warehouse
#         stock_entry.to_warehouse = work_order.fg_warehouse
#         stock_entry.project = work_order.project
#         # Get Leftover
#         stock_entry.leftover = work_order.leftover_qty

#     stock_entry.set_stock_entry_type()
#     stock_entry.get_items()
#     stock_entry.set_serial_no_batch_for_finished_good()
#     # add leftover to items
#     if flt(stock_entry.leftover) > 0:
#         item_dict = stock_entry.get("items")
#         for d in item_dict:
#             if not d.is_finished_item:
#                 continue
#             se_child = stock_entry.append("items")
#             se_child.s_warehouse = None
#             se_child.t_warehouse = wip_warehouse
#             se_child.item_code = d.get("item_code")
#             se_child.uom = d.get("uom")
#             se_child.stock_uom = d.get("stock_uom")
#             se_child.qty = flt(stock_entry.leftover, d.precision("qty"))
#             d.qty = flt((flt(d.qty) - flt(stock_entry.leftover)), d.precision("qty"))
#             se_child.allow_alternative_item = d.get("allow_alternative_item", 0)
#             se_child.subcontracted_item = d.get("main_item_code")
#             se_child.cost_center = d.get("cost_center")
#             se_child.is_finished_item = d.get("is_finished_item")
#             se_child.is_scrap_item = d.get("is_scrap_item")
#             se_child.is_process_loss = d.get("is_process_loss")
#             se_child.conversion_factor = flt(d.get("conversion_factor"))
#             se_child.transfer_qty = flt(
#                 flt(stock_entry.leftover, d.precision("qty"))
#                 * flt(d.get("conversion_factor")),
#                 d.precision("qty"),
#             )
#             se_child.bom_no = d.get("bom_no")
#             se_child.job_card_item = d.get("job_card_item")
#             se_child.batch_no = d.get("batch_no")
#             break
#     stock_entry.get_stock_and_rate()
#     return stock_entry.as_dict()

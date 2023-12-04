from contextlib import suppress
import this
from frappe import _
import frappe


def custom_jobcard_get_data(data):
    data["transactions"].append(
        {"label": _("Manufacturing"), "items": ["Leftover"]},
    )

    return data


def custom_workorder_get_data(data):
    # data.append("dynamic_links")
    # data["fieldname"] = ("work_order", "production_item")
    # doc =pare frappe.get_doc("Work Order", this.name)
    data["dynamic_links"] = dict(
        # {"reference_name": ["حثيرات Zednad-500", "item"]},
        # {"reference_name": ["{work_order.production_item}", "item"]},
        {"reference_name": ["Work Order", "reference_doctype"]},
    )

    return data

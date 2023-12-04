import frappe
from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry
from frappe.utils.data import cint


class StockEntry(StockEntry):
    def set_batch_no_from_work_order_for_fg(self):
        for d in self.get("items"):
            # current_item = frappe.get_cached_doc("item", d.item_code)
            if not d.is_finished_item:
                continue
            # current_item = frappe.get_doc("item", d.item_code)
            can_create_new_batch = frappe.db.get_value(
                "Item", d.item_code, "create_new_batch"
            )
            if (
                d.bom_no
                and d.is_finished_item
                and (self.purpose == "Manufacture")
                and self.work_order
                and (can_create_new_batch == 0)
            ):
                if not d.batch_no:
                    wo = frappe.get_cached_doc("Work Order", self.work_order)
                    if wo.batch_no:
                        d.batch_no = wo.batch_no

    def set_serial_no_batch_for_finished_good(self):
        super().set_serial_no_batch_for_finished_good()
        self.set_batch_no_from_work_order_for_fg()

    def validate_fg_completed_qty(self):
        pass

    def validate_finished_goods(self):
        pass

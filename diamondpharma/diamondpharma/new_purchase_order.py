import frappe
from frappe.utils import flt, getdate, formatdate

def validate_budget_limits(doc, method):
    # Track processed employee-account combinations to avoid duplicate checks
    checked_budgets = {}

    # Get the current fiscal year based on your business logic
    current_fiscal_year = str(getdate().year)  # Assuming fiscal year is the current year
    frappe.msgprint(f"Current Fiscal Year: {current_fiscal_year}")

    for item in doc.items:
        employee = item.employee
        expense_account = item.expense_account
        budget_key = f"{employee}-{expense_account}"

        if budget_key in checked_budgets:
            continue

        # Fetch the Budget associated with the employee and fiscal year
        budget = frappe.get_doc("Budget", {"employee": employee, "fiscal_year": current_fiscal_year, "docstatus": 1})

        # Check if budget is found
        if not budget:
            frappe.throw(f"No budget found for employee {employee} in fiscal year {current_fiscal_year}.")

        frappe.msgprint(f"Budget Name: {budget.name}")  # Show budget name if found

        account_record = next((acc for acc in budget.accounts if acc.account == expense_account), None)
        if not account_record:
            frappe.throw(f"Expense account {expense_account} not found in the budget for employee {employee}.")

        distribution = frappe.get_doc("Monthly Distribution", budget.monthly_distribution)
        
        # Use the transaction_date from the Purchase Order document
        month = formatdate(getdate(doc.transaction_date), "MMMM")

        month_percentage = next((dist.percentage_allocation for dist in distribution.percentages if dist.month == month), None)
        
        if month_percentage is None:
            frappe.throw(f"No percentage allocation found for {month} in the monthly distribution {distribution.name}.")

        monthly_budget_allowed = flt(account_record.budget_amount) * (flt(month_percentage) / 100)

        total_for_employee_account = sum(
            flt(i.base_amount) for i in doc.items if i.employee == employee and i.expense_account == expense_account
        )

        if total_for_employee_account > monthly_budget_allowed:
            frappe.throw(
                f"Total amount {total_for_employee_account} for employee {employee} on account {expense_account} "
                f"exceeds the allowed monthly budget of {monthly_budget_allowed} for {month}."
            )

        checked_budgets[budget_key] = True


import frappe
from frappe.utils import flt, getdate, formatdate

def validate_budget_limitsss(poname='PUR-ORD-2024-00059'):
    # Fetch the Purchase Order document
    doc = frappe.get_doc("Purchase Order", poname)
    
    # Track processed employee-account combinations to avoid duplicate checks
    checked_budgets = {}

    # Get the current fiscal year based on your business logic
    current_fiscal_year = str(getdate().year)  # Assuming fiscal year is the current year
    frappe.msgprint(f"Current Fiscal Year: {current_fiscal_year}")

    for item in doc.items:
        employee = item.employee
        expense_account = item.expense_account
        budget_key = f"{employee}-{expense_account}"

        if budget_key in checked_budgets:
            continue

        budget = frappe.get_doc("Budget", {"employee": employee, "fiscal_year": current_fiscal_year, "docstatus": 1})
        print(budget.name)
        # Check if budget is found
        if not budget:
            frappe.throw(f"No budget found for employee {employee} in fiscal year {current_fiscal_year}.")
        
        frappe.msgprint(f"Budget Name: {budget.name}")  # Show budget name if found

        account_record = next((acc for acc in budget.accounts if acc.account == expense_account), None)
        if not account_record:
            frappe.throw(f"Expense account {expense_account} not found in the budget for employee {employee}.")

        distribution = frappe.get_doc("Monthly Distribution", budget.monthly_distribution)
        print(doc.transaction_date)
        month = formatdate(getdate(doc.transaction_date), "MMMM")

        month_percentage = next((dist.percentage_allocation for dist in distribution.percentages if dist.month == month), None)
        
        if month_percentage is None:
            frappe.throw(f"No percentage allocation found for {month} in the monthly distribution {distribution.name}.")

        monthly_budget_allowed = flt(account_record.budget_amount) * (flt(month_percentage) / 100)

        total_for_employee_account = sum(
            flt(i.base_amount) for i in doc.items if i.employee == employee and i.expense_account == expense_account
        )

        if total_for_employee_account > monthly_budget_allowed:
            frappe.throw(
                f"Total amount {total_for_employee_account} for employee {employee} on account {expense_account} "
                f"exceeds the allowed monthly budget of {monthly_budget_allowed} for {month}."
            )

        checked_budgets[budget_key] = True



def check_purchase_order_item(doc, method=None):

    if frappe.session.user == "lawrence.darawi@admin.dpharma.sy":
        employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "employee_name")
        
        if not employee:
            frappe.throw("No employee record found for this user.")
        
        if len(doc.items) > 0:
            for item in doc.items:
                item.employee = employee
                frappe.logger().info(f"Assigned employee: {employee} to item: {item.name}")


def check_purchase_order_item22(po_name = 'PUR-ORD-2024-00066'):
    # Fetch the current user
    user = 'lawrence.darawi@admin.dpharma.sy'
    print(user)
    if user == "lawrence.darawi@admin.dpharma.sy":
        # Fetch employee name
        employee = frappe.db.get_value("Employee", {"user_id": user}, "employee_name")

        if not employee:
            frappe.throw("No employee record found for this user.")


        # Fetch purchase order items
        po_items = frappe.get_all("Purchase Order Item", filters={"parent": po_name}, fields=["name"])

        if po_items:
            for item in po_items:
                print(item["name"])
                # Load the Purchase Order Item document and set the employee
                po_item_doc = frappe.get_doc("Purchase Order Item", item["name"])
                po_item_doc.db_set("employee", employee)
                print("po_item_doc.employee",po_item_doc.employee)
            frappe.msgprint("Employee field updated for all Purchase Order Items.")
        else:
            frappe.msgprint("No items found in the Purchase Order Item table.")
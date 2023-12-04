from erpnext.accounts.doctype.budget.budget import Budget, DuplicateBudgetError
import frappe


class MultiBudget(Budget):
    def validate_duplicate(self):
        budget_against_field = frappe.scrub(self.budget_against)
        budget_against = self.get(budget_against_field)

        accounts = [d.account for d in self.accounts] or []
        existing_budget = frappe.db.sql(
            """
			select
				b.name, ba.account from `tabBudget` b, `tabBudget Account` ba
			where
				ba.parent = b.name and b.docstatus < 2 and b.company = %s and %s=%s and
				b.fiscal_year=%s and b.name != %s and ba.account in (%s) """
            % (
                "%s",
                budget_against_field,
                "%s",
                "%s",
                "%s",
                ",".join(["%s"] * len(accounts)),
            ),
            (self.company, budget_against, self.fiscal_year, self.name)
            + tuple(accounts),
            as_dict=1,
        )

        for d in existing_budget:
            frappe.throw(
                frappe._(
                    "xxxxxxxxxxAnother Budget record '{0}' already exists against {1} '{2}' and account '{3}' for fiscal year {4}"
                ).format(
                    d.name,
                    self.budget_against,
                    budget_against,
                    d.account,
                    self.fiscal_year,
                ),
                DuplicateBudgetError,
            )

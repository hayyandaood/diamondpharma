import frappe

from frappe.utils import add_days, cint, cstr, date_diff, formatdate, getdate,flt
from frappe.query_builder import Criterion
from frappe.query_builder.functions import Sum, Count

from frappe.query_builder import DocType

from erpnext.payroll.doctype.salary_slip.salary_slip import SalarySlip

import datetime



#def calculate_tax(amount):

#	tax_amount = 0


#	if amount > 50000 and amount < 80001  : 
#		tax_amount = (amount - 50000) * 0.04
#	if amount > 80000 and amount < 110001  :
	# 1200 
#		tax_amount = 1200 + (amount- 80000) * 0.06
	# 1200 + 1800 
#	if amount > 110000 and amount < 140001  :
#		tax_amount = 3000 + (amount- 110000) * 0.08
	# 1200 + 1800 + 2400 
#	if amount > 140000 and amount < 170001  :
#		tax_amount = 5400 + (amount - 140000) * 0.1 
	# 1200 + 1800 + 2400 + 3000 
#	if amount > 170000 and amount < 200001  :
#		tax_amount = 8400 + ( amount - 170000) * 0.12
	# 1200 + 1800 + 2400 + 3000 + 3600 
#	if amount > 200000 and amount < 230001  :
#		tax_amount = 12000 + (amount - 200000) * 0.14
	# 1200 + 1800 + 2400 + 3000 + 3600 + 4200 
#	if amount > 230000 and amount < 260001  :
#		tax_amount = 16200 + ( amount - 230000) * 0.16
	# 1200 + 1800 + 2400 + 3000 + 3600 + 4200 + 4800 
#	if amount > 260000   :
#		tax_amount = 21000 + ( amount - 260000) * 0.18


#	return tax_amount

def calculate_tax(amount):

	tax_amount = 0


	if amount > 185940 and amount < 250001  : 
		tax_amount = (amount - 185940) * 0.05
	if amount > 250000 and amount < 450001  :
	# 3203 
		tax_amount = 3203 + (amount- 250000) * 0.07
	# 3203 + 14000 
	if amount > 450000 and amount < 650001  :
		tax_amount = 17203 + (amount- 450000) * 0.09
	# 3203 + 14000 + 18000 
	if amount > 650000 and amount < 850001  :
		tax_amount = 35203 + (amount - 650000) * 0.11 
	# 3203 + 14000 + 18000 + 22000 
	if amount > 850000 and amount < 1100001  :
		tax_amount = 57203 + ( amount - 850000) * 0.13
	# 3203 + 14000 + 18000 + 22000 + 32500 
	if amount > 1100000  :
		tax_amount = 89703 + (amount - 1100000) * 0.15
	# 3203 + 14000 + 18000 + 22000 + 32500 + 165000 


	return tax_amount 
    
def adjust_dates(from_date):

	start_from = getdate(from_date)
	month = start_from.month
	day = 16
	if month == 1:
		month = 12
		year = start_from.year -1 
	else :
		month = month - 1
		year = start_from.year

	from_start = (datetime.datetime(year,month,day)).strftime("%Y-%m-%d")
	to_end =  (datetime.datetime(start_from.year,start_from.month,15)).strftime("%Y-%m-%d")
	
	return from_start, to_end




def retrive_totals(employee, from_start,base_amount):

	from_date, to_date = adjust_dates(from_start)

	income_tax = calculate_tax(base_amount) 
#	income_tax = income_tax + (10 - (income_tax % 10))

	Attendance_doctype = frappe.qb.DocType("Attendance")
	count_all = Count('*').as_("total_lwp")
	leave_type_field = frappe.qb.Field("leave_type")
	employee_field = frappe.qb.Field("employee")
	attendance_date_field = frappe.qb.Field("attendance_date")



			# .where((Attendance_doctype.status == 'On Leave') & (leave_type_field == 'اجازة بلا راتب'))

	result = (
			frappe.qb.from_(Attendance_doctype)
			.select(count_all)
			.where((Attendance_doctype.status == 'On Leave') & 
		  			(leave_type_field == 'اجازة بلا راتب'))
			.where((Attendance_doctype.docstatus == 1) & (employee_field == employee))
			.where(attendance_date_field[from_date:to_date])	  
			).run(as_dict=True)

	total_lwp = flt(result[0].total_lwp) if result else 0



	total = frappe.db.sql(
		"""
		SELECT sum((overtime_duration / 60) * (overtime_percentage / 100)) as total_overtime
		FROM `tabAttendance`
		WHERE status = 'Present' and
			docstatus = 1 and employee = %s and
			attendance_date between %s and %s 
		""", (employee, from_date,to_date),
		as_dict = 1 
		)


	total_overtime = flt(total[0].total_overtime) if total else 0 # calculated in minutes


	result = {
	 	"total_lwp" : total_lwp, 
		"total_absent" : 0,
		"total_overtime": total_overtime ,  
		"income_tax": income_tax,
	}
	return result

class SalarySlipOverride(SalarySlip):
	def get_data_for_eval(self):

		data, default_data = super().get_data_for_eval()
		
		totals = retrive_totals(
			data.get("employee"),
			data.get("start_date"),
			data.get("base") * 0.93 )
		
		data.update(totals)
		default_data.update(totals)

#		print(data)
		return data, default_data




@frappe.whitelist()
def get_base_and_var_employee(employee, fromDate) :


	sal_structue_assignment = frappe.db.sql(
		"""
		SELECT base,variable
		FROM `tabSalary Structure Assignment`
		WHERE docstatus = 1 and employee = %s and
			from_date <= %s 
		""", (employee, fromDate),
		as_dict = 1 
		)
	base = sal_structue_assignment[0].base
	variable = sal_structue_assignment[0].variable

	return base, variable
	
	
	
	
def get_totals_validate(doc , method=None):
	print("salary slip validate :",doc.name , method)
	amt = 0
	if (doc.net_pay):
		if ( doc.net_pay % 500 ):
			amt = 500 - (doc.net_pay % 500)
			amt += doc.net_pay
			doc.net_pay=amt
			doc.rounded_total=amt
	


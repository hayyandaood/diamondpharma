# Copyright (c) 2023, Diamond pharma and contributors
# For license information, please see license.txt

import frappe
import datetime
import json

from frappe.model.document import Document
from frappe.utils import getdate




class AssetCheckTool(Document):
	pass


@frappe.whitelist()
def load_assets(asset_category = None, periodic = None) :


	filters = {	"periodic" : periodic   }
	if asset_category :
		filters["asset_category"] = asset_category


	asset_list = frappe.get_list(
		"Asset Check Template", 
		fields=["asset", "asset_name",
	  			"asset_category", "item_code",
				"periodic","description"], 
		filters={
			"asset_category" : asset_category,
			"periodic" : periodic
		}
	)


	return {"asset_list": asset_list}


@frappe.whitelist()
def mark_assets( asset_list = None, asset_category = None,
			date = None , periodic = None) :
	
	if isinstance(asset_list, str):
		asset_list = json.loads(asset_list)
	
	print(asset_list)

	for asset in asset_list:

		Asset_Check_Detail = frappe.get_doc(
			dict(
				doctype="Asset Check Detail",
				asset_category = asset_category,
				asset = asset,
				periodic=periodic,
				date_checked= getdate(date),
				checked=1,
			)
		)
		Asset_Check_Detail.insert()
		Asset_Check_Detail.submit()

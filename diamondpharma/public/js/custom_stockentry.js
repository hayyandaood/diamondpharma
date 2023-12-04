frappe.ui.form.on('Stock Entry', {
    refresh: function (frm) {
        if (frm.doc.purpose == "Material Transfer for Manufacture") {
            frm.trigger('filterChildFields')//(frm, "leftover_usage_list", "production_item", "production_item", "leftover");
        };
    },
    filterChildFields: function (frm)//, tableName, fieldTrigger, fieldName, fieldFiltered)
    {
        frm.fields_dict["leftover_usage_list"].grid.get_field("leftover").get_query = function (doc, cdt, cdn) {
            let child = locals[cdt][cdn];
            return {
                filters: [
                    //["production_item", '=', child["production_item"]]
                    ["production_item", '=', frm.doc.production_item],
                    ["remaining_quantity_for_use", '>', 0],
                    //["qty", '>', 'used_qty '],
                    ["docstatus", '=', 1],
                    ["name", 'not in', frm.doc.leftover_usage_list.map(leftover_usage_list => leftover_usage_list.leftover)],

                ]
            }
        }
    },
    explode_leftover_items: function (frm) {
        frm.doc.leftover_usage_items = [];
        frm.refresh_field("leftover_usage_items");
        console.log(frm.fields_dict);

        if (frm.doc.leftover_usage_list.length != 0) {

            let leftover_user_selection = Object.keys(frm.doc.leftover_usage_list).map(function (key) {
                return {
                    "leftover": frm.doc.leftover_usage_list[key].leftover,
                    "qty_percent": frm.doc.leftover_usage_list[key].qty_percent
                };
            });
            // loop inside leftover_user_selection child table
            for (let i = 0; i < leftover_user_selection.length; i++) {
                if (leftover_user_selection[i].leftover) {
                    console.log(leftover_user_selection[i].leftover);
                    if (leftover_user_selection[i].qty_percent > 0) {
                        /////////////////////////////////////

                        let qty_percent = leftover_user_selection[i].qty_percent;
                        frappe.call({
                            method: "diamondpharma.diamondpharma.doctype.leftover.leftover.get_Leftover_Items",
                            async: false,
                            args: {
                                docnameparam: leftover_user_selection[i].leftover,
                                qty_percent: qty_percent
                            },
                            callback: function (r) {
                                if (r.message) {
                                    let leftover_doc_items = r.message;
                                    console.log(leftover_doc_items);

                                    for (let m = 0; m < leftover_doc_items.length; m++) {
                                        let found = false;
                                        for (let j = 0; j < frm.doc.leftover_usage_items.length; j++) {
                                            if (frm.doc.leftover_usage_items[j].item_code) {
                                                if (frm.doc.leftover_usage_items[j].item_code == leftover_doc_items[m].item_code) {
                                                    found = true;
                                                    frm.doc.leftover_usage_items[j].qty = flt(frm.doc.leftover_usage_items[j].qty) + ((flt(leftover_doc_items[m].qty) * flt(leftover_user_selection[i].qty_percent)) / 100);
                                                    break;
                                                };
                                            };
                                        };
                                        if (!found) {
                                            let childTable = frm.add_child("leftover_usage_items");
                                            childTable.item_code = leftover_doc_items[m].item_code;
                                            childTable.item_name = leftover_doc_items[m].item_name;
                                            childTable.qty = ((flt(leftover_doc_items[m].qty) * flt(leftover_user_selection[i].qty_percent)) / 100);
                                            childTable.uom = leftover_doc_items[m].uom;
                                        };

                                    };
                                }
                            }
                        });
                    };
                };
            };
            frm.refresh_field("leftover_usage_items");

        };
        console.log(frm);
        console.log(frm.doc);
        frm.parent.frm.call({
            doc: frm.parent.frm.doc,
            freeze: true,
            method: "get_items",
            callback: function (r) {
                //   debugger;
                if (!r.exc) refresh_field("items");
                if (frm.parent.frm.doc.bom_no) attach_bom_items(frm.parent.frm.doc.bom_no);
                if (frm.doc.leftover_usage_items.length > 0) {
                    for (let l = 0; l < frm.doc.items.length; l++) {
                        for (let k = 0; k < frm.doc.items.length; k++) {
                            if (frm.doc.items[k].item_code == frm.doc.leftover_usage_items[l].item_code) {
                                frm.doc.items[k].qty = frm.doc.items[k].qty - frm.doc.leftover_usage_items[l].qty;
                            };
                        };
                    };
                    frm.refresh_field("items");
                };
            }
        });
    },
});
frappe.ui.form.on("Leftover Usage", {
    leftover: function (frm, cdt, cdn) {
        //debugger;
        console.log("leftover field linked: ", " ", cdt, " ", cdn);
        let row = locals[cdt][cdn];
        console.log("leftover : ", " ", row.leftover);
        console.log("row: ", " ", row);
        //  console.log("leftover.remaining_quantity_for_use: ", " ", leftover.remaining_quantity_for_use);

        frappe.call({
            method: "diamondpharma.diamondpharma.doctype.leftover.leftover.get_Leftover_Usage_Qty",
            args: {
                docnameparam: row.leftover,
            },
            callback: function (r) {
                console.log(r.exc);
                if (!r.exc && r.message) {
                    console.log("r: ", " ", r);

                    frappe.model.set_value(cdt, cdn, 'qty_for_use', parseFloat(row.original_qty) - parseFloat(r.message));

                }
            }
        });
        frappe.model.set_value(cdt, cdn, 'qty', parseFloat(row.qty_for_use));
        frappe.model.set_value(cdt, cdn, 'qty_percent', (100 * parseFloat(row.qty)) / parseFloat(row.original_qty));
        frm.trigger('qty');
        frm.fields_dict.explode_leftover_items.onclick();

    },
    leftover_usage_list_add: function (frm) {
        frm.fields_dict.explode_leftover_items.onclick();
    },
    leftover_usage_list_remove: function (frm) {
        frm.fields_dict.explode_leftover_items.onclick();
    },
    qty: function (frm, cdt, cdn) {
        // let row = locals[cdt][cdn];
        frm.refresh_field("leftover_usage_items");
        let row = locals[cdt][cdn];
        if (row.leftover) {
            // debugger;
            if ((row.qty <= 0) || (!row.qty)) {
                frappe.model.set_value(cdt, cdn, 'qty', parseFloat(row.qty_for_use));
            } else {
                if (parseFloat(row.qty) > parseFloat(row.qty_for_use)) {
                    frappe.show_alert({ message: __('qty: {0} ,is more than remaining quantity for use: {1}', [row.qty, row.qty_for_use]), indicator: 'red' });
                    row.qty = row.qty_for_use;
                };
            };
            frappe.model.set_value(cdt, cdn, 'qty_percent', (100 * parseFloat(row.qty)) / parseFloat(row.original_qty));
            frm.refresh_field("leftover_usage_list");
            if (row.leftover) {
                console.log("*************************", row);
                frappe.db.get_doc('Leftover', row.leftover).then((ldoc) => {
                    console.log(ldoc);
                });
            };
            //  frm.trigger('get_leftover_usage_items');
            frm.refresh_field("leftover_usage_items");
            frm.fields_dict.explode_leftover_items.onclick();
            console.log(frm);
        };
    },
});
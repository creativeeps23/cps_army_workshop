frappe.query_reports["Army Item Batteries Detailed Report"] = {
    "filters": [
        {
            "fieldname": "item_code",
            "label": __("كود المنتج"),
            "fieldtype": "Data",
            "width": 80
        },
        {
            "fieldname": "item_name",
            "label": __("اسم المنتج"),
            "fieldtype": "Data",
            "width": 80
        },
   
        {
            "fieldname": "capacity",
            "label": __("السعة"),
            "fieldtype": "Data",
            "width": 80
        },
        {
            "fieldname": "xx_number",
            "label": __("XX Number"),
            "fieldtype": "Data",
            "width": 80
        },
        {
            "fieldname": "status",
            "label": __("الحالة"),
            "fieldtype": "Select",
            "options": "\nمتوفر\nمنخفض\nنافذ",
            "width": 80
        }
    ]
};

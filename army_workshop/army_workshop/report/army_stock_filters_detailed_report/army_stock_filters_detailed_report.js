frappe.query_reports["Army Stock Filters Detailed Report"] = {
    "filters": [
        {
            "fieldname": "item_code",
            "label": __("باركود"),
            "fieldtype": "Data",
            "width": 80
        },
        {
            "fieldname": "item_name",
            "label": __("اسم الصنف"),
            "fieldtype": "Link",
            "options": "Army Stock Filters",
            "width": 80
        },
        
        {
            "fieldname": "xx_number",
            "label": __("XX Number"),
            "fieldtype": "Data",
            "width": 80
        },
        {
            "fieldname": "part_number",
            "label": __("رقم العينة"),
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

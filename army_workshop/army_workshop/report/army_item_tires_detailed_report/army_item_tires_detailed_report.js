frappe.query_reports["Army Item Tires Detailed Report"] = {
    "filters": [
        {
            "fieldname": "item_code",
            "label": __("كود الصنف"),
            "fieldtype": "Data",
            "width": 80
        },
        {
            "fieldname": "item_name",
            "label": __("اسم الصنف"),
            "fieldtype": "Link", 
                        "options": "Army Item Tires", 
            "width": 80
        },
       
       
        {
            "fieldname": "المقاس", 
            "label": __("المقاس"),
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

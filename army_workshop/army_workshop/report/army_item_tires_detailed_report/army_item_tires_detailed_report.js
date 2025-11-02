frappe.query_reports["Army Item Tires Detailed Report"] = {
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

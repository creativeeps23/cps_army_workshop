// Copyright (c) 2025, Creative Programming Solutions and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Ongoing Repair Equipments"] = {
	// Copyright (c) 2025, Creative Programming Solutions and contributors
// For license information, please see license.txt
/* eslint-disable */


    "filters": [
        {
            "fieldname": "department",
            "label": "الإدارة",
            "fieldtype": "Link",
            "options": "Army Department"
        },
        {
            "fieldname": "subunit",
            "label": "الوحدة الفرعية",
            "fieldtype": "Link",
            "options": "Army Subunit"
        },
        {
            "fieldname": "location",
            "label": "الموقع",
            "fieldtype": "Link",
            "options": "Army Location"
        },
        {
            "fieldname": "technician_name",
            "label": "اسم الفني",
            "fieldtype": "Data"
        },
      
        {
            "fieldname": "administration_approval_category",
            "label": "تصديق الإدارة",
            "fieldtype": "Select",
            "options": "\nWith Administration Approval\nWithout Administration Approval"
        },
        {
            "fieldname": "entry_from_date",
            "label": "من تاريخ الدخول",
            "fieldtype": "Date"
        },
        {
            "fieldname": "entry_to_date",
            "label": "إلى تاريخ الدخول",
            "fieldtype": "Date"
        },
               {
            "fieldname": "show_delegate",
            "label": "عرض بيانات المندوب",
            "fieldtype": "Check",
            "default": 0
        }
    ]
};

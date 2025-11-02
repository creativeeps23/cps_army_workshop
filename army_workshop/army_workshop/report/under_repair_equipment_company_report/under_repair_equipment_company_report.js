// Copyright (c) 2025, Creative Programming Solutions and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Under Repair Equipment Company Report"] = {
	// Copyright (c) 2025, Creative Programming Solutions and contributors
// For license information, please see license.txt
/* eslint-disable */


	// Copyright (c) 2025, Creative Programming Solutions and contributors
// For license information, please see license.txt
/* eslint-disable */



    "filters": [
        {
            "fieldname": "unit_name",
            "label": "الوحدة",
            "fieldtype": "Link",
            "options": "Army Unit"
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
            "fieldname": "manufacture",
            "label": "الشركة المصنعة",
            "fieldtype": "Link",
            "options": "Manufacture"
        },
        {
            "fieldname": "delegated_name",
            "label": "اسم المندوب",
            "fieldtype": "Link",
            "options": "Delegate"
        },
        {
            "fieldname": "repair_type",
            "label": "نوع الإصلاح",
            "fieldtype": "Select",
            "options": "\nمعدة\nمجموعة"
        },
        {
            "fieldname": "administration_approval_category",
            "label": "نوع التصديق",
            "fieldtype": "Select",
            "options": "\nWith Administration Approval\nWithout Administration Approval"
        },
        {
            "fieldname": "from_date",
            "label": "من تاريخ الدخول",
            "fieldtype": "Date"
        },
        {
            "fieldname": "to_date",
            "label": "إلى تاريخ الدخول",
            "fieldtype": "Date"
        },
        {
            "fieldname": "show_delegate",
            "label": "عرض بيانات المندوب",
            "fieldtype": "Check",
            "default": 0
        },
        {
            "fieldname": "show_technical_team",
            "label": "عرض بيانات الفريق الفني",
            "fieldtype": "Check",
            "default": 0
        }
      
    ]
};

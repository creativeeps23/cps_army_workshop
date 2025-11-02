// Copyright (c) 2025, Creative Programming Solutions and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Repaired Groups Only Report"] = {
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
            "label": "مكان التواجد",
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
            "fieldname": "status",
            "label": "الحالة",
            "fieldtype": "Select",
            "options": "\nتم الإصلاح\nتم التسليم"
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
        },
        {
            "fieldname": "show_actions",
            "label": "عرض الأعمال المنفذة",
            "fieldtype": "Check",
            "default": 0
        }
    ]
};

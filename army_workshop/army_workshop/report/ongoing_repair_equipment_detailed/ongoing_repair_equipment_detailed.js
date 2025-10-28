// Copyright (c) 2025, Creative Programming Solutions and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Ongoing Repair Equipment Detailed"] = {

    filters: [
        {
            fieldname: "department",
            label: "الإدارة",
            fieldtype: "Link",
            options: "Army Department"
        },
        {
            fieldname: "sub_unit",
            label: "الوحدة الفرعية",
            fieldtype: "Link",
            options: "Army Subunit"
        },
        {
            fieldname: "location",
            label: "الموقع",
            fieldtype: "Data"
        },
        {
            fieldname: "administration_approval_category",
            label: "نوع تصديق الإدارة",
            fieldtype: "Select",
            options: "\nWith Administration Approval\nWithout Administration Approval"
        },
        {
            fieldname: "repair_type",
            label: "نوع الإصلاح",
            fieldtype: "Select",
            options: "\nمعدة\nمجموعة"
        },
        {
            fieldname: "show_delegate_details",
            label: "عرض بيانات المندوب",
            fieldtype: "Check",
            default: 0
        }
    ]
};

// Copyright (c) 2025, Creative Programming Solutions and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Incomplete Repair Equipment Detailed"] = {
	"filters": [
        {
            "fieldname": "report_type",
            "label": __("نوع التقرير"),
            "fieldtype": "Select",
            "options": "\nتقرير الإصلاحات الجارية\nتقرير المستندات الناقصة",
            "default": "تقرير الإصلاحات الجارية",
            "on_change: function() {
                frappe.query_report.refresh();
            }
        },
        {
            "fieldname": "department",
            "label": __("الإدارة"),
            "fieldtype": "Link",
            "options": "Army Department"
        },
        {
            "fieldname": "subunit",
            "label": __("الوحدة الفرعية"),
            "fieldtype": "Link",
            "options": "Army Subunit"
        },
        {
            "fieldname": "location",
            "label": __("الموقع"),
            "fieldtype": "Link",
            "options": "Army Location"
        },
        {
            "fieldname": "technician_name",
            "label": __("اسم الفني"),
            "fieldtype": "Data"
        },
        {
            "fieldname": "repair_type",
            "label": __("نوع الإصلاح"),
            "fieldtype": "Select",
            "options": "\nمعدات\nمجموعة"
        },
        {
            "fieldname": "administration_approval_category",
            "label": __("تصديق الإدارة"),
            "fieldtype": "Select",
            "options": "\nWith Administration Approval\nWithout Administration Approval"
        },
        {
            "fieldname": "entry_from_date",
            "label": __("من تاريخ الدخول"),
            "fieldtype": "Date"
        },
        {
            "fieldname": "entry_to_date",
            "label": __("إلى تاريخ الدخول"),
            "fieldtype": "Date"
        },
        {
            "fieldname": "leave_from_date",
            "label": __("من تاريخ الخروج"),
            "fieldtype": "Date"
        },
        {
            "fieldname": "leave_to_date",
            "label": __("إلى تاريخ الخروج"),
            "fieldtype": "Date"
        },
        {
            "fieldname": "show_delegate",
            "label": __("عرض بيانات المندوب"),
            "fieldtype": "Check",
            "default": 0
        },
        {
            "fieldname": "show_technical_team",
            "label": __("عرض بيانات الفريق الفني"),
            "fieldtype": "Check",
            "default": 0
        },
        {
            "fieldname": "show_actions",
            "label": __("عرض بيانات الأعمال"),
            "fieldtype": "Check",
            "default": 0
        }
    ],

    "onload: function(report) {
        // إضافة زر لتصدير تقرير المستندات الناقصة
        report.page.add_inner_button(__("تصدير تقرير المستندات الناقصة"), function() {
            var filters = report.get_values();
            filters.report_type = "missing_documents";
            frappe.query_report.load_report(report, filters);
        });
        
        // إضافة زر للعودة للتقرير الرئيسي
        report.page.add_inner_button(__("العودة لتقرير الإصلاحات"), function() {
            var filters = report.get_values();
            filters.report_type = "ongoing_repair";
            frappe.query_report.load_report(report, filters);
        });
    }
};
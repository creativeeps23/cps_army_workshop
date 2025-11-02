frappe.query_reports["Equipment and Groups Delivered"] = {


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
            "fieldname": "repair_type",
            "label": "نوع الإصلاح",
            "fieldtype": "Select",
            "options": "\nمعدات\nمجموعة",

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
            "fieldname": "leave_from_date",
            "label": "من تاريخ الخروج",
            "fieldtype": "Date"
        },
        {
            "fieldname": "leave_to_date",
            "label": "إلى تاريخ الخروج",
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
            "default": 1
        },
        {
            "fieldname": "show_actions",
            "label": "عرض الأعمال المنفذة",
            "fieldtype": "Check",
            "default": 0
        }
    ]
};


import frappe

def execute(filters=None):
    filters = filters or {}

    conditions = []
    if filters.get("department"):
        conditions.append("er.department = %(department)s")
    if filters.get("subunit"):
        conditions.append("er.subunit = %(subunit)s")
    if filters.get("location"):
        conditions.append("er.location = %(location)s")
    if filters.get("repair_type"):
        conditions.append("er.repair_type = %(repair_type)s")
    if filters.get("administration_approval_category"):
        conditions.append("er.administration_approval_category = %(administration_approval_category)s")

    condition_sql = " AND ".join(conditions)
    if condition_sql:
        condition_sql = "WHERE " + condition_sql

    query = f"""
        SELECT
            er.name AS repair_id,
            er.equipment_name AS equipment_name,
            er.equipment_model AS equipment_model,
            er.army_number AS army_number,
            er.chassis_number AS chassis_number,
            er.unit_name AS unit_name,
            er.subunit AS subunit,
            er.department AS department,
            er.location AS location,
            er.entry_date,
            er.leave_date,
            er.manufacture,
            CASE 
                WHEN er.administration_approval_category = 'With Administration Approval' THEN er.work_order_number
                ELSE er.work_order_number1
            END AS work_order_number,
            CASE 
                WHEN er.administration_approval_category = 'With Administration Approval' THEN er.work_order_date
                ELSE er.work_order_date1
            END AS work_order_date,
            er.administration_approval_category,
            d.delegated_name,
            d.degree__grade,
            d.delegated_army_number,
            d.mobile_phone,
            GROUP_CONCAT(DISTINCT a.البيان SEPARATOR ', ') AS work_done
        FROM 
            `tabEquipment Repair` er
        LEFT JOIN `tabDelegate` d ON d.name = er.delegated_name
        LEFT JOIN `tabActions` a ON a.parent = er.name
        {condition_sql}
        GROUP BY er.name
        ORDER BY er.entry_date DESC
    """

    data = frappe.db.sql(query, filters, as_dict=True)

    # لو المستخدم مش عايز يشوف بيانات المندوب
    if not filters.get("show_delegate_details"):
        for row in data:
            row["delegated_name"] = None
            row["degree__grade"] = None
            row["delegated_army_number"] = None
            row["mobile_phone"] = None

    columns = [
        {"label": "رقم الإصلاح", "fieldname": "repair_id", "fieldtype": "Link", "options": "Equipment Repair"},
        {"label": "اسم المعدة", "fieldname": "equipment_name", "fieldtype": "Data"},
        {"label": "موديل المعدة", "fieldname": "equipment_model", "fieldtype": "Data"},
        {"label": "رقم الجيش", "fieldname": "army_number", "fieldtype": "Data"},
        {"label": "رقم الشاسيه", "fieldname": "chassis_number", "fieldtype": "Data"},
        {"label": "الإدارة", "fieldname": "department", "fieldtype": "Data"},
        {"label": "الوحدة", "fieldname": "unit_name", "fieldtype": "Data"},
        {"label": "الوحدة الفرعية", "fieldname": "subunit", "fieldtype": "Data"},
        {"label": "الموقع", "fieldname": "location", "fieldtype": "Data"},
        {"label": "تاريخ الدخول", "fieldname": "entry_date", "fieldtype": "Date"},
        {"label": "تاريخ الخروج", "fieldname": "leave_date", "fieldtype": "Date"},
        {"label": "نوع تصديق الإدارة", "fieldname": "administration_approval_category", "fieldtype": "Data"},
        {"label": "تاريخ إذن الشغل", "fieldname": "work_order_date", "fieldtype": "Date"},
        {"label": "رقم إذن الشغل", "fieldname": "work_order_number", "fieldtype": "Data"},
        {"label": "الشركة المصنعة", "fieldname": "manufacture", "fieldtype": "Data"},
        {"label": "تفاصيل الأعمال المنفذة", "fieldname": "work_done", "fieldtype": "Data"},
    ]

    # أعرض بيانات المندوب لو التشيك بوكس متعلم
    if filters.get("show_delegate_details"):
        columns += [
            {"label": "اسم المندوب", "fieldname": "delegated_name", "fieldtype": "Data"},
            {"label": "الرتبة", "fieldname": "degree__grade", "fieldtype": "Data"},
            {"label": "الرقم العسكري", "fieldname": "delegated_army_number", "fieldtype": "Data"},
            {"label": "رقم التليفون", "fieldname": "mobile_phone", "fieldtype": "Data"},
        ]

    return columns, data


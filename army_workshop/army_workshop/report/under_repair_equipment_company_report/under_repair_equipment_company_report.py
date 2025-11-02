import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}

    # Build conditions dynamically
    conditions = [
        "er.status IN ('جار الإصلاح - طرف خارجي')",
        "er.repair_type = 'معدة'"  # شرط ثابت لجلب المعدات فقط
    ]

    query_filters = {}

    if filters.get("unit_name"):
        conditions.append("er.unit_name = %(unit_name)s")
        query_filters["unit_name"] = filters.get("unit_name")
    if filters.get("subunit"):
        conditions.append("er.subunit = %(subunit)s")
        query_filters["subunit"] = filters.get("subunit")
    if filters.get("location"):
        conditions.append("er.location = %(location)s")
        query_filters["location"] = filters.get("location")
    if filters.get("manufacture"):
        conditions.append("er.manufacture = %(manufacture)s")
        query_filters["manufacture"] = filters.get("manufacture")
    if filters.get("delegated_name"):
        conditions.append("er.delegated_name = %(delegated_name)s")
        query_filters["delegated_name"] = filters.get("delegated_name")
    if filters.get("administration_approval_category"):
        conditions.append("er.administration_approval_category = %(administration_approval_category)s")
        query_filters["administration_approval_category"] = filters.get("administration_approval_category")
    if filters.get("repair_type"):
        conditions.append("er.repair_type = %(repair_type)s")
        query_filters["repair_type"] = filters.get("repair_type")
    
    # فلترة التاريخ من - إلى
    if filters.get("from_date") and filters.get("to_date"): 
        conditions.append("er.entry_date BETWEEN %(from_date)s AND %(to_date)s")
        query_filters["from_date"] = filters.get("from_date")
        query_filters["to_date"] = filters.get("to_date")

    condition_sql = " AND ".join(conditions)
    if condition_sql:
        condition_sql = "WHERE " + condition_sql

    # Select fields based on filters
    select_fields = """
        er.name AS repair_id,
        er.equipment_name,
        er.equipment_model,
        er.army_number,
        er.chassis_number,
        er.manufacture,
        er.unit_name,
        er.subunit,
        er.location,
        er.entry_date,
        er.leave_date,
        er.status,
        er.repair_type,
        er.administration_approval_category,
        CASE 
            WHEN er.administration_approval_category = 'With Administration Approval' THEN er.work_order_number
            ELSE er.work_order_number1
        END as work_order_number,
        CASE 
            WHEN er.administration_approval_category = 'With Administration Approval' THEN er.work_order_date
            ELSE er.work_order_date1
        END as work_order_date
    """

    # Add delegate fields if show_delegate is selected
    if filters.get("show_delegate"):
        select_fields += """,
            er.delegated_name,
            er.delegated_army_number,
            er.degree__grade,
            er.mobile_phone AS delegated_mobile
        """

    # Add technical team fields only if show_technical_team is selected
    if filters.get("show_technical_team"):
        select_fields += """,
            tt.name1 AS technician_name,
            tt.degree AS technician_degree,
            tt.job AS technician_job,
            tt.army_number AS technician_army_number,
            tt.mobile_phone AS technician_mobile
        """

    # بناء الاستعلام بناءً على اختيار عرض الفريق الفني
    if filters.get("show_technical_team"):
        query = f"""
            SELECT
                {select_fields}
            FROM
                `tabEquipment Repair` er
            LEFT JOIN
                `tabTechnical Team List` tt ON er.name = tt.parent
            {condition_sql}
            ORDER BY er.entry_date DESC, tt.idx
        """
    else:
        query = f"""
            SELECT
                {select_fields}
            FROM
                `tabEquipment Repair` er
            {condition_sql}
            ORDER BY er.entry_date DESC
        """

    data = frappe.db.sql(query, query_filters, as_dict=True)

    # If requested, attach actions data
    if filters.get("show_actions"):
        data = add_actions_data(data)



    # Define columns
    columns = [
        {"label": "رقم الإصلاح", "fieldname": "repair_id", "fieldtype": "Link", "options": "Equipment Repair", "width": 130},
        {"label": "اسم المعدة", "fieldname": "equipment_name", "fieldtype": "Data", "width": 150},
        {"label": "طراز المعدة", "fieldname": "equipment_model", "fieldtype": "Data", "width": 130},
        {"label": "الرقم العسكري", "fieldname": "army_number", "fieldtype": "Data", "width": 130},
        {"label": "رقم الشاسيه", "fieldname": "chassis_number", "fieldtype": "Data", "width": 130},
        {"label": "الشركة المصنعة", "fieldname": "manufacture", "fieldtype": "Data", "width": 140},
        {"label": "الوحدة", "fieldname": "unit_name", "fieldtype": "Data", "width": 130},
        {"label": "الوحدة الفرعية", "fieldname": "subunit", "fieldtype": "Data", "width": 130},
        {"label": "الموقع", "fieldname": "location", "fieldtype": "Data", "width": 130},
        {"label": "نوع الإصلاح", "fieldname": "repair_type", "fieldtype": "Data", "width": 120},
        {"label": "نوع التصديق", "fieldname": "administration_approval_category", "fieldtype": "Data", "width": 150},
        {"label": "رقم أمر الشغل", "fieldname": "work_order_number", "fieldtype": "Data", "width": 130},
        {"label": "تاريخ أمر الشغل", "fieldname": "work_order_date", "fieldtype": "Date", "width": 120},
        {"label": "تاريخ الدخول", "fieldname": "entry_date", "fieldtype": "Date", "width": 120},
        {"label": "تاريخ الخروج", "fieldname": "leave_date", "fieldtype": "Date", "width": 120},
        {"label": "الحالة", "fieldname": "status", "fieldtype": "Data", "width": 150},
    ]

    if filters.get("show_delegate"):
        columns += [
            {"label": "اسم المندوب", "fieldname": "delegated_name", "fieldtype": "Data", "width": 150},
            {"label": "الرتبة", "fieldname": "degree__grade", "fieldtype": "Data", "width": 120},
            {"label": "الرقم العسكري", "fieldname": "delegated_army_number", "fieldtype": "Data", "width": 120},
            {"label": "رقم الهاتف", "fieldname": "delegated_mobile", "fieldtype": "Data", "width": 120},
        ]

    if filters.get("show_technical_team"):
        columns += [
            {"label": "اسم الفني", "fieldname": "technician_name", "fieldtype": "Data", "width": 150},
            {"label": "الرتبة (الفني)", "fieldname": "technician_degree", "fieldtype": "Data", "width": 120},
            {"label": "الوظيفة", "fieldname": "technician_job", "fieldtype": "Data", "width": 150},
            {"label": "الرقم العسكري", "fieldname": "technician_army_number", "fieldtype": "Data", "width": 120},
            {"label": "رقم الهاتف", "fieldname": "technician_mobile", "fieldtype": "Data", "width": 120},
        ]

    if filters.get("show_actions"):
        columns += [
            {"label": "الأعمال الميكانيكية", "fieldname": "mechanic_actions", "fieldtype": "Data", "width": 200},
            {"label": "الأعمال الكهربائية", "fieldname": "electric_actions", "fieldtype": "Data", "width": 200},
            {"label": "أعمال أخرى", "fieldname": "other_actions", "fieldtype": "Data", "width": 200},
        ]


    return columns, data, None


def add_actions_data(data):
    """
    إضافة بيانات الأعمال (Actions) لكل سجل
    """
    for record in data:
        repair_id = record["repair_id"]
        
        try:
            # استخدام frappe.get_doc للحصول على الوثيقة والجداول الفرعية
            doc = frappe.get_doc("Equipment Repair", repair_id)
            
            # تجميع الأعمال الميكانيكية
            mechanic_actions = []
            for action in doc.get("mechanic", []):
                action_text = action.get("work_description") or action.get("action") or ""
                notes_text = action.get("notes") or ""
                if action_text:
                    mechanic_actions.append(f"{action_text} ({notes_text})" if notes_text else action_text)
            
            # تجميع الأعمال الكهربائية
            electric_actions = []
            for action in doc.get("electric", []):
                action_text = action.get("work_description") or action.get("action") or ""
                notes_text = action.get("notes") or ""
                if action_text:
                    electric_actions.append(f"{action_text} ({notes_text})" if notes_text else action_text)
            
            # تجميع الأعمال الأخرى
            other_actions = []
            for action in doc.get("others", []):
                action_text = action.get("work_description") or action.get("action") or ""
                notes_text = action.get("notes") or ""
                if action_text:
                    other_actions.append(f"{action_text} ({notes_text})" if notes_text else action_text)
            
            # إضافة البيانات للسجل
            record["mechanic_actions"] = " | ".join(mechanic_actions) if mechanic_actions else ""
            record["electric_actions"] = " | ".join(electric_actions) if electric_actions else ""
            record["other_actions"] = " | ".join(other_actions) if other_actions else ""
            
        except Exception as e:
            # في حالة وجود خطأ، نعرض رسالة خطأ بدلاً من تعطيل التقرير
            record["mechanic_actions"] = f"خطأ في جلب البيانات: {str(e)}"
            record["electric_actions"] = ""
            record["other_actions"] = ""
    
    return data




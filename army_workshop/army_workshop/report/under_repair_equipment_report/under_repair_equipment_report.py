import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}

    # Build conditions dynamically - تم إصلاح الخطأ هنا
    conditions = ["er.status = 'جار الإصلاح'"]  # استخدام الحالة المطلوبة فقط
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

    # Build chart مع إضافة الفلتر
    chart = get_chart_data(filters)

    # Define columns
    columns = [
        {"label": "رقم الإصلاح", "fieldname": "repair_id", "fieldtype": "Link", "options": "Equipment Repair", "width": 130},
        {"label": "اسم المعدة", "fieldname": "equipment_name", "fieldtype": "Data", "width": 150},
        {"label": "طراز المعدة", "fieldname": "equipment_model", "fieldtype": "Data", "width": 130},
        {"label": "رقم الجيش", "fieldname": "army_number", "fieldtype": "Data", "width": 130},
        {"label": "رقم الشاسيه", "fieldname": "chassis_number", "fieldtype": "Data", "width": 130},
        {"label": "الشركة المصنعة", "fieldname": "manufacture", "fieldtype": "Data", "width": 140},
        {"label": "الوحدة", "fieldname": "unit_name", "fieldtype": "Data", "width": 130},
        {"label": "الوحدة الفرعية", "fieldname": "subunit", "fieldtype": "Data", "width": 130},
        {"label": "الموقع", "fieldname": "location", "fieldtype": "Data", "width": 130},
        {"label": "نوع الإصلاح", "fieldname": "repair_type", "fieldtype": "Data", "width": 120},
        {"label": "نوع التصديق", "fieldname": "administration_approval_category", "fieldtype": "Data", "width": 150},
        {"label": "رقم اذن الشغل", "fieldname": "work_order_number", "fieldtype": "Data", "width": 130},
        {"label": "تاريخ اذن الشغل", "fieldname": "work_order_date", "fieldtype": "Date", "width": 120},
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

    # Build summary
    summary = get_summary(data)

    return columns, data, None, chart, summary


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


def get_summary(data):
    if not data:
        return []

    total_records = len(data)
    
    # Count by repair type
    equipment_count = len([d for d in data if d.get("repair_type") == "معدة"])
    group_count = len([d for d in data if d.get("repair_type") == "مجموعة"])
    
    # Count unique technicians only if technician_name exists in data
    technicians = set()
    for record in data:
        if record.get('technician_name'):
            technicians.add(record.get('technician_name'))
    
    summary = [
        {"label": "إجمالي السجلات", "value": total_records, "indicator": "Blue"},
        {"label": "المعدات قيد الإصلاح", "value": equipment_count, "indicator": "Orange"},
        {"label": "المجموعات قيد الإصلاح", "value": group_count, "indicator": "Purple"},
    ]
    
    # إضافة عدد الفنيين فقط إذا كانت بيانات الفنيين معروضة
    if technicians:
        summary.insert(1, {"label": "عدد الفنيين", "value": len(technicians), "indicator": "Green"})
    
    return summary


def get_chart_data(filters=None):
    """
    بناء الرسم البياني مع إمكانية التصفية حسب الشركة المصنعة
    """
    filters = filters or {}
    
    # بناء شروط التصفية للرسم البياني
    chart_filters = {"status": "جار الإصلاح"}
    
    # إضافة فلتر الشركة المصنعة إذا كان موجوداً
    if filters.get("manufacture"):
        chart_filters["manufacture"] = filters.get("manufacture")
    
    # بيانات الرسم البياني
    data_points = []

    # إجمالي المعدّات والمجموعات
    total_equipment = frappe.db.count(
        "Equipment Repair", {**chart_filters, "repair_type": "معدة"}
    )
    total_groups = frappe.db.count(
        "Equipment Repair", {**chart_filters, "repair_type": "مجموعة"}
    )

    data_points.append({"label": "إجمالي المعدات", "value": total_equipment})
    data_points.append({"label": "إجمالي المجموعات", "value": total_groups})

    # إحصائيات حسب الشركات المصنعة
    manufacturers = frappe.db.get_all(
        "Equipment Repair",
        filters=chart_filters,
        fields=["manufacture", "repair_type", "COUNT(*) as count"],
        group_by="manufacture, repair_type",
        order_by="manufacture"
    )

    # تجميع البيانات حسب الشركة المصنعة
    manufacturer_data = {}
    for item in manufacturers:
        manufacture = item.get("manufacture") or "غير محدد"
        repair_type = item.get("repair_type")
        count = item.get("count", 0)
        
        if manufacture not in manufacturer_data:
            manufacturer_data[manufacture] = {"معدة": 0, "مجموعة": 0}
        
        manufacturer_data[manufacture][repair_type] = count

    # إضافة بيانات الشركات المصنعة للرسم البياني
    for manufacture, counts in manufacturer_data.items():
        equipment_count = counts.get("معدة", 0)
        group_count = counts.get("مجموعة", 0)
        
        if equipment_count > 0:
            data_points.append({"label": f"{manufacture} - معدات", "value": equipment_count})
        if group_count > 0:
            data_points.append({"label": f"{manufacture} - مجموعات", "value": group_count})

    # إذا لم يكن هناك فلتر، نضيف إحصائيات إضافية
    if not filters.get("manufacture"):
        # عدد المعدات حسب الوحدة (أعلى 5 وحدات)
        units_data = frappe.db.get_all(
            "Equipment Repair",
            filters=chart_filters,
            fields=["unit_name", "COUNT(*) as count"],
            group_by="unit_name",
            order_by="count DESC",
            limit=5
        )
        
        for unit in units_data:
            unit_name = unit.get("unit_name") or "غير محدد"
            count = unit.get("count", 0)
            data_points.append({"label": f"الوحدة: {unit_name}", "value": count})

    labels = [d["label"] for d in data_points]
    values = [d["value"] for d in data_points]

    chart = {
        "data": {
            "labels": labels,
            "datasets": [{"name": "عدد المعدات", "values": values}],
        },
        "type": "bar",
        "colors": ["#2490ef"],
        "height": 300,
    }
    return chart

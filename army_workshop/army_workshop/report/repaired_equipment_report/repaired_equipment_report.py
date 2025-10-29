import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}

    # Build conditions dynamically (common filters)
    conditions = []
    query_filters = {}

    # default statuses for this report (repaired / delivered)
    default_statuses = ("تم الإصلاح", "تم التسليم")

    # If user selected a specific status, use it, otherwise use default statuses
    if filters.get("status"):
        conditions.append("er.status = %(status)s")
        query_filters["status"] = filters.get("status")
        statuses_for_counts = (filters.get("status"),)
    else:
        conditions.append("er.status IN %(statuses)s")
        query_filters["statuses"] = default_statuses
        statuses_for_counts = default_statuses

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

    # date range (from_date / to_date)
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

    # Main query: get repaired/delivered records
    query = f"""
        SELECT
            {select_fields}
        FROM
            `tabEquipment Repair` er
        {condition_sql}
        ORDER BY er.entry_date DESC
    """

    data = frappe.db.sql(query, query_filters, as_dict=True)

    # If requested, attach technical team details per repair record (aggregate as a string)
    if filters.get("show_technical_team"):
        for row in data:
            team_rows = frappe.db.sql("""
                SELECT
                    name1 AS technician_name,
                    degree AS technician_degree,
                    job AS technician_job,
                    army_number AS technician_army_number,
                    mobile_phone AS technician_mobile
                FROM `tabTechnical Team List`
                WHERE parent = %s
                ORDER BY idx
            """, row["repair_id"], as_dict=True)

            if team_rows:
                row["technical_team"] = "; ".join(
                    [f"{t['technician_name']} ({t['technician_degree'] or ''} - {t['technician_job'] or ''} - {t['technician_army_number'] or ''})" for t in team_rows]
                )
            else:
                row["technical_team"] = ""

    # If requested, attach actions data
    if filters.get("show_actions"):
        data = add_actions_data(data)

    # Build summary and chart (respecting other filters, counts restricted to statuses_for_counts)
    summary, chart = build_summary_and_chart(query_filters, statuses_for_counts, filters.get("status"))

    # Columns
    columns = [
        {"label": "رقم الإصلاح", "fieldname": "repair_id", "fieldtype": "Link", "options": "Equipment Repair", "width": 130},
        {"label": "اسم المعدة", "fieldname": "equipment_name", "fieldtype": "Data", "width": 160},
        {"label": "طراز المعدة", "fieldname": "equipment_model", "fieldtype": "Data", "width": 120},
        {"label": "الرقم العسكري", "fieldname": "army_number", "fieldtype": "Data", "width": 110},
        {"label": "رقم الشاسيه", "fieldname": "chassis_number", "fieldtype": "Data", "width": 130},
        {"label": "الشركة المصنعة", "fieldname": "manufacture", "fieldtype": "Data", "width": 140},
        {"label": "الوحدة", "fieldname": "unit_name", "fieldtype": "Data", "width": 120},
        {"label": "الوحدة الفرعية", "fieldname": "subunit", "fieldtype": "Data", "width": 120},
        {"label": "مكان التواجد", "fieldname": "location", "fieldtype": "Data", "width": 120},
        {"label": "نوع الإصلاح", "fieldname": "repair_type", "fieldtype": "Data", "width": 100},
        {"label": "نوع التصديق", "fieldname": "administration_approval_category", "fieldtype": "Data", "width": 140},
        {"label": "رقم أمر الشغل", "fieldname": "work_order_number", "fieldtype": "Data", "width": 130},
        {"label": "تاريخ أمر الشغل", "fieldname": "work_order_date", "fieldtype": "Date", "width": 120},
        {"label": "تاريخ الدخول", "fieldname": "entry_date", "fieldtype": "Date", "width": 110},
        {"label": "تاريخ الخروج", "fieldname": "leave_date", "fieldtype": "Date", "width": 110},
        {"label": "الحالة", "fieldname": "status", "fieldtype": "Data", "width": 130},
    ]

    if filters.get("show_delegate"):
        columns += [
            {"label": "اسم المندوب", "fieldname": "delegated_name", "fieldtype": "Data", "width": 150},
            {"label": "الرقم العسكري للمندوب", "fieldname": "delegated_army_number", "fieldtype": "Data", "width": 140},
            {"label": "الرتبة / الدرجة", "fieldname": "degree__grade", "fieldtype": "Data", "width": 120},
            {"label": "موبايل المندوب", "fieldname": "delegated_mobile", "fieldtype": "Data", "width": 120},
        ]

    if filters.get("show_technical_team"):
        columns += [
            {"label": "الفريق الفني (الاسم - رتبة - وظيفة - رقم عسكري)", "fieldname": "technical_team", "fieldtype": "Data", "width": 300},
        ]

    if filters.get("show_actions"):
        columns += [
            {"label": "الأعمال الميكانيكية", "fieldname": "mechanic_actions", "fieldtype": "Data", "width": 200},
            {"label": "الأعمال الكهربائية", "fieldname": "electric_actions", "fieldtype": "Data", "width": 200},
            {"label": "أعمال أخرى", "fieldname": "other_actions", "fieldtype": "Data", "width": 200},
        ]

    # return columns, data, (no message), chart, summary
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
                action_text = action.get("البيان") or action.get("action") or ""
                notes_text = action.get("notes") or ""
                if action_text:
                    mechanic_actions.append(f"{action_text} ({notes_text})" if notes_text else action_text)
            
            # تجميع الأعمال الكهربائية
            electric_actions = []
            for action in doc.get("electric", []):
                action_text = action.get("البيان") or action.get("action") or ""
                notes_text = action.get("notes") or ""
                if action_text:
                    electric_actions.append(f"{action_text} ({notes_text})" if notes_text else action_text)
            
            # تجميع الأعمال الأخرى
            other_actions = []
            for action in doc.get("others", []):
                action_text = action.get("البيان") or action.get("action") or ""
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


def build_summary_and_chart(common_filters, statuses, selected_status=None):
    """
    Build summary counts and chart.
    common_filters: dict containing filters like unit_name, manufacture, from_date, to_date, delegated_name, administration_approval_category, repair_type (if provided)
    statuses: tuple/list of statuses to consider for counting (e.g. ("تم الإصلاح","تم التسليم"))
    selected_status: if a specific status was selected in filters
    """
    # Create a clean filters dict for frappe.db.count
    count_filters = {}
    
    # Copy relevant filters from common_filters
    for key in ['unit_name', 'subunit', 'location', 'manufacture', 'delegated_name', 
                'administration_approval_category', 'repair_type', 'from_date', 'to_date']:
        if key in common_filters:
            count_filters[key] = common_filters[key]
    
    # Handle status filter - use the appropriate key based on what was used in the main query
    if selected_status:
        # If a specific status was selected, use 'status' key
        count_filters['status'] = selected_status
        statuses_for_counting = [selected_status]
    else:
        # If no specific status, use 'statuses' key with tuple
        count_filters['status'] = ['in', list(statuses)]
        statuses_for_counting = statuses

    # helper to build condition dict for frappe.db.count
    def count_records(extra_filters=None):
        qf = count_filters.copy()
        if extra_filters:
            qf.update(extra_filters)
        return frappe.db.count("Equipment Repair", qf)

    # totals across both statuses in `statuses_for_counting`
    total_equipment = count_records({"repair_type": "معدة"})
    total_groups = count_records({"repair_type": "مجموعة"})

    # تغيير ترتيب البيانات في التشارت حسب الطلب
    data_points = []
    
    # المعدات أولاً مع جميع الحالات
    for s in statuses_for_counting:
        eq_count = count_records({"status": s, "repair_type": "معدة"})
        data_points.append({"label": f"المعدات - {s}", "value": eq_count})
    
    # ثم المجموعات مع جميع الحالات
    for s in statuses_for_counting:
        grp_count = count_records({"status": s, "repair_type": "مجموعة"})
        data_points.append({"label": f"المجموعات - {s}", "value": grp_count})

    # build summary list
    summary = [
        {"label": "إجمالي المعدات (معدة)", "value": total_equipment, "indicator": "Blue"},
        {"label": "إجمالي المجموعات (مجموعة)", "value": total_groups, "indicator": "Blue"},
    ]
    # append the detailed data points
    for dp in data_points:
        summary.append({"label": dp["label"], "value": dp["value"], "indicator": "Green"})

    # chart: show the same data points (detailed breakdown)
    labels = [dp["label"] for dp in data_points]
    values = [dp["value"] for dp in data_points]

    chart = {
        "data": {
            "labels": labels,
            "datasets": [{"name": "عدد", "values": values}]
        },
        "type": "bar"
    }

    return summary, chart

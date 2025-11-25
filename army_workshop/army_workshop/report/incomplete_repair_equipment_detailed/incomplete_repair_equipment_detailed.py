import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}

    # تحديد نوع التقرير المطلوب
    report_type = filters.get("report_type", "ongoing_repair")  # ongoing_repair أو missing_documents
    
    if report_type == "missing_documents":
        return get_missing_documents_report(filters)
    else:
        return get_ongoing_repair_report(filters)


def get_ongoing_repair_report(filters):
    columns = get_columns(filters)
    data = get_data(filters)
    
    # إضافة بيانات الأعمال (Actions) لكل سجل
    if filters.get("show_actions"):
        data = add_actions_data(data)
    
    summary = get_summary(data)
    chart = get_chart(data)

    return columns, data, None, chart, summary


def get_missing_documents_report(filters):
    columns = get_missing_documents_columns()
    data = get_missing_documents_data(filters)
    summary = get_missing_documents_summary(data)
    
    return columns, data, None, None, summary


def get_missing_documents_columns():
    return [
        {"label": _("رقم الإصلاح"), "fieldname": "repair_id", "fieldtype": "Link", "options": "Equipment Repair", "width": 120},
        {"label": _("اسم المعدة"), "fieldname": "equipment_name", "fieldtype": "Data", "width": 150},
        {"label": _("الوحدة"), "fieldname": "unit_name", "fieldtype": "Data", "width": 120},
        {"label": _("تصديق الإدارة"), "fieldname": "administration_approval_category", "fieldtype": "Data", "width": 150},
        {"label": _("الحالة"), "fieldname": "status", "fieldtype": "Data", "width": 120},
        
        # أعمدة المستندات
        {"label": _("خطاب المهمة"), "fieldname": "mission_letter_status", "fieldtype": "Data", "width": 100},
        {"label": _("تصديق الإدارة"), "fieldname": "administration_approval_status", "fieldtype": "Data", "width": 100},
        {"label": _("شهادة سجل المعدة"), "fieldname": "equipment_log_certificate_status", "fieldtype": "Data", "width": 120},
        {"label": _("نموذج 3at"), "fieldname": "form_3at_status", "fieldtype": "Data", "width": 100},
        {"label": _("نموذج 4at"), "fieldname": "form_4at_status", "fieldtype": "Data", "width": 100},
        {"label": _("شهادة إتمام الإصلاح"), "fieldname": "certificate_of_repair_completion_status", "fieldtype": "Data", "width": 140},
        {"label": _("نموذج قبول الخصم"), "fieldname": "deduction_acceptance_form_status", "fieldtype": "Data", "width": 140},
        {"label": _("صورة البطاقة"), "fieldname": "id_card_copy_status", "fieldtype": "Data", "width": 100},
        
        # العمود الرئيسي للمستندات الناقصة
        {"label": _("المستندات الناقصة"), "fieldname": "missing_documents", "fieldtype": "Data", "width": 300},
    ]


def get_missing_documents_data(filters):
    conditions = ["er.administration_approval_category = 'With Administration Approval'"]
    query_params = {}

    # Add conditions based on filters
    if filters.get("department"):
        conditions.append("er.department = %(department)s")
        query_params["department"] = filters.get("department")
    
    if filters.get("subunit"):
        conditions.append("er.subunit = %(subunit)s")
        query_params["subunit"] = filters.get("subunit")
    
    if filters.get("location"):
        conditions.append("er.location = %(location)s")
        query_params["location"] = filters.get("location")
    
    if filters.get("repair_type"):
        repair_type = "معدة" if filters.get("repair_type") == "معدات" else filters.get("repair_type")
        conditions.append("er.repair_type = %(repair_type)s")
        query_params["repair_type"] = repair_type

    # Build the WHERE clause
    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT
            er.name as repair_id,
            er.equipment_name,
            er.unit_name,
            er.administration_approval_category,
            er.status,
            er.mission_letter,
            er.administration_approval,
            er.equipment_log_certificate,
            er.form_3at,
            er.form_4at,
            er.certificate_of_repair_completion,
            er.deduction_acceptance_form,
            er.id_card_copy
        FROM
            `tabEquipment Repair` er
        WHERE
            {where_clause}
        ORDER BY
            er.entry_date DESC
    """

    data = frappe.db.sql(query, query_params, as_dict=True)
    
    # معالجة البيانات وإضافة حالة كل مستند وقائمة المستندات الناقصة
    for record in data:
        record = add_document_status(record)
    
    return data


def add_document_status(record):
    """إضافة حالة كل مستند وقائمة المستندات الناقصة للسجل"""
    
    # قائمة المستندات المطلوبة
    documents = [
        ('mission_letter', 'خطاب المهمة'),
        ('administration_approval', 'تصديق الإدارة'),
        ('equipment_log_certificate', 'شهادة سجل المعدة'),
        ('form_3at', 'نموذج 3at'),
        ('form_4at', 'نموذج 4at'),
        ('certificate_of_repair_completion', 'شهادة إتمام الإصلاح'),
        ('deduction_acceptance_form', 'نموذج قبول الخصم'),
        ('id_card_copy', 'صورة البطاقة')
    ]
    
    missing_docs = []
    
    for doc_field, doc_name in documents:
        status_field = f"{doc_field}_status"
        
        # التحقق من وجود المستند (إذا كانت القيمة ليست فارغة أو صفر)
        if record.get(doc_field):
            record[status_field] = "ناجح"
        else:
            record[status_field] = "ناقص"
            missing_docs.append(doc_name)
    
    # إضافة قائمة المستندات الناقصة
    record["missing_documents"] = "، ".join(missing_docs) if missing_docs else "جميع المستندات مكتملة"
    
    return record


def get_missing_documents_summary(data):
    if not data:
        return []

    total_records = len(data)
    
    # حساب المستندات الناقصة
    missing_counts = {
        'mission_letter': 0,
        'administration_approval': 0,
        'equipment_log_certificate': 0,
        'form_3at': 0,
        'form_4at': 0,
        'certificate_of_repair_completion': 0,
        'deduction_acceptance_form': 0,
        'id_card_copy': 0
    }
    
    for record in data:
        for doc_field in missing_counts.keys():
            if record.get(f"{doc_field}_status") == "ناقص":
                missing_counts[doc_field] += 1
    
    summary = [
        {"label": "إجمالي السجلات", "value": total_records, "indicator": "Blue"},
        {"label": "السجلات ذات مستندات ناقصة", "value": len([d for d in data if d.missing_documents != "جميع المستندات مكتملة"]), "indicator": "Red"},
    ]
    
    # إضافة إحصائيات للمستندات الأكثر نقصاً
    most_missing = sorted(missing_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    for doc_field, count in most_missing:
        if count > 0:
            doc_name = {
                'mission_letter': 'خطاب المهمة',
                'administration_approval': 'تصديق الإدارة', 
                'equipment_log_certificate': 'شهادة سجل المعدة',
                'form_3at': 'نموذج 3at',
                'form_4at': 'نموذج 4at',
                'certificate_of_repair_completion': 'شهادة إتمام الإصلاح',
                'deduction_acceptance_form': 'نموذج قبول الخصم',
                'id_card_copy': 'صورة البطاقة'
            }.get(doc_field, doc_field)
            
            summary.append({"label": f"ناقص - {doc_name}", "value": count, "indicator": "Orange"})
    
    return summary


# الدوال الأصلية (بدون تغيير)
def get_columns(filters):
    columns = [
        {"label": _("رقم الإصلاح"), "fieldname": "repair_id", "fieldtype": "Link", "options": "Equipment Repair", "width": 120},
        {"label": _("اسم المعدة"), "fieldname": "equipment_name", "fieldtype": "Data", "width": 150},
        {"label": _("طراز المعدة"), "fieldname": "equipment_model", "fieldtype": "Data", "width": 120},
        {"label": _("رقم الشاسيه"), "fieldname": "chassis_number", "fieldtype": "Data", "width": 130},
        {"label": _("الشركة المصنعة"), "fieldname": "manufacture", "fieldtype": "Data", "width": 140},
        {"label": _("الرقم العسكري للمعدة"), "fieldname": "army_number", "fieldtype": "Data", "width": 100},
        {"label": _("الوحدة"), "fieldname": "unit_name", "fieldtype": "Data", "width": 120},
        {"label": _("الوحدة الفرعية"), "fieldname": "subunit", "fieldtype": "Data", "width": 120},
        {"label": _("الموقع"), "fieldname": "location", "fieldtype": "Data", "width": 120},
        {"label": _("الإدارة"), "fieldname": "department", "fieldtype": "Data", "width": 120},
        {"label": _("نوع الإصلاح"), "fieldname": "repair_type", "fieldtype": "Data", "width": 100},
        {"label": _("تصديق الإدارة"), "fieldname": "administration_approval_category", "fieldtype": "Data", "width": 150},
        {"label": _("تاريخ الدخول"), "fieldname": "entry_date", "fieldtype": "Date", "width": 110},
        {"label": _("تاريخ الخروج"), "fieldname": "leave_date", "fieldtype": "Date", "width": 110},
        {"label": _("الحالة"), "fieldname": "status", "fieldtype": "Data", "width": 120},
    ]



    columns.extend([
        {"label": _("رقم اذن الشغل"), "fieldname": "work_order_number", "fieldtype": "Data", "width": 130},
        {"label": _("تاريخ اذن الشغل"), "fieldname": "work_order_date", "fieldtype": "Date", "width": 120},
    ])


    # إضافة أعمدة المندوب إذا تم اختيار عرض بيانات المندوب
    if filters.get("show_delegate"):
        columns.extend([
            {"label": _("اسم المندوب"), "fieldname": "delegated_name", "fieldtype": "Data", "width": 150},
            {"label": _("الرقم العسكري للمندوب"), "fieldname": "delegated_army_number", "fieldtype": "Data", "width": 140},
            {"label": _("الرتبة / الدرجة"), "fieldname": "degree__grade", "fieldtype": "Data", "width": 120},
            {"label": _("موبايل المندوب"), "fieldname": "delegated_mobile", "fieldtype": "Data", "width": 120},
        ])

    # إضافة أعمدة الفريق الفني فقط إذا تم اختيار عرض بيانات الفريق الفني
    if filters.get("show_technical_team"):
        columns.extend([
            {"label": _("اسم الفني"), "fieldname": "technician_name", "fieldtype": "Data", "width": 150},
            {"label": _("رتبة الفني"), "fieldname": "technician_degree", "fieldtype": "Data", "width": 120},
            {"label": _("وظيفة الفني"), "fieldname": "technician_job", "fieldtype": "Data", "width": 120},
            {"label": _("الرقم العسكري الفني"), "fieldname": "technician_army_number", "fieldtype": "Data", "width": 120},
            {"label": _("موبايل الفني"), "fieldname": "technician_mobile", "fieldtype": "Data", "width": 120},
        ])

    # إضافة أعمدة الأعمال إذا تم اختيار عرضها
    if filters.get("show_actions"):
        columns.extend([
            {"label": _("الأعمال الميكانيكية"), "fieldname": "mechanic_actions", "fieldtype": "Data", "width": 200},
            {"label": _("الأعمال الكهربائية"), "fieldname": "electric_actions", "fieldtype": "Data", "width": 200},
            {"label": _("أعمال أخرى"), "fieldname": "other_actions", "fieldtype": "Data", "width": 200},
        ])

    return columns


def get_data(filters):
    conditions = ["er.status = 'قيد الفحص'"]  # الحالة ثابتة = قيد الفحص
    query_params = {}

    # Add conditions based on filters
    if filters.get("department"):
        conditions.append("er.department = %(department)s")
        query_params["department"] = filters.get("department")
    
    if filters.get("subunit"):
        conditions.append("er.subunit = %(subunit)s")
        query_params["subunit"] = filters.get("subunit")
    
    if filters.get("location"):
        conditions.append("er.location = %(location)s")
        query_params["location"] = filters.get("location")
    
    if filters.get("technician_name"):
        conditions.append("tt.name1 LIKE %(technician_name)s")
        query_params["technician_name"] = f"%{filters.get('technician_name')}%"
    
    if filters.get("repair_type"):
        # Convert "معدات" to "معدة" to match the field value
        repair_type = "معدة" if filters.get("repair_type") == "معدات" else filters.get("repair_type")
        conditions.append("er.repair_type = %(repair_type)s")
        query_params["repair_type"] = repair_type
    
    if filters.get("administration_approval_category"):
        # استخدام القيمة مباشرة بدون تحويل
        conditions.append("er.administration_approval_category = %(administration_approval_category)s")
        query_params["administration_approval_category"] = filters.get("administration_approval_category")
    
    # Date range for entry_date (تاريخ الدخول)
    if filters.get("entry_from_date") and filters.get("entry_to_date"):
        conditions.append("er.entry_date BETWEEN %(entry_from_date)s AND %(entry_to_date)s")
        query_params["entry_from_date"] = filters.get("entry_from_date")
        query_params["entry_to_date"] = filters.get("entry_to_date")
    elif filters.get("entry_from_date"):
        conditions.append("er.entry_date >= %(entry_from_date)s")
        query_params["entry_from_date"] = filters.get("entry_from_date")
    elif filters.get("entry_to_date"):
        conditions.append("er.entry_date <= %(entry_to_date)s")
        query_params["entry_to_date"] = filters.get("entry_to_date")
    
    # Date range for leave_date (تاريخ الخروج)
    if filters.get("leave_from_date") and filters.get("leave_to_date"):
        conditions.append("er.leave_date BETWEEN %(leave_from_date)s AND %(leave_to_date)s")
        query_params["leave_from_date"] = filters.get("leave_from_date")
        query_params["leave_to_date"] = filters.get("leave_to_date")
    elif filters.get("leave_from_date"):
        conditions.append("er.leave_date >= %(leave_from_date)s")
        query_params["leave_from_date"] = filters.get("leave_from_date")
    elif filters.get("leave_to_date"):
        conditions.append("er.leave_date <= %(leave_to_date)s")
        query_params["leave_to_date"] = filters.get("leave_to_date")

    # Build the WHERE clause
    where_clause = " AND ".join(conditions)

    # Select fields based on filters
    select_fields = """
        er.name as repair_id,
        er.equipment_name,
        er.equipment_model,
        er.chassis_number,
        er.manufacture,
        er.army_number,
        er.unit_name,
        er.subunit,
        er.location,
        er.department,
        er.repair_type,
        er.administration_approval_category,
        er.entry_date,
        er.leave_date,
        er.status,
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
            er.mobile_phone as delegated_mobile
        """

    # Add technical team fields only if show_technical_team is selected
    if filters.get("show_technical_team"):
        select_fields += """,
            tt.name1 as technician_name,
            tt.degree as technician_degree,
            tt.job as technician_job,
            tt.army_number as technician_army_number,
            tt.mobile_phone as technician_mobile
        """

    # بناء الاستعلام بناءً على اختيار عرض الفريق الفني
    if filters.get("show_technical_team"):
        query = f"""
            SELECT
                {select_fields}
            FROM
                `tabEquipment Repair` er
            INNER JOIN
                `tabTechnical Team List` tt ON er.name = tt.parent
            WHERE
                {where_clause}
            ORDER BY
                er.entry_date DESC, tt.idx
        """
    else:
        query = f"""
            SELECT
                {select_fields}
            FROM
                `tabEquipment Repair` er
            WHERE
                {where_clause}
            ORDER BY
                er.entry_date DESC
        """

    data = frappe.db.sql(query, query_params, as_dict=True)
    return data

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


def get_summary(data):
    if not data:
        return []

    total_records = len(data)
    
    # Count by repair type
    equipment_count = len([d for d in data if d.repair_type == "معدة"])
    group_count = len([d for d in data if d.repair_type == "مجموعة"])
    
    # Count unique technicians only if technician_name exists in data
    technicians = set()
    for record in data:
        if hasattr(record, 'technician_name') and record.technician_name:
            technicians.add(record.technician_name)
    
    summary = [
        {"label": "إجمالي السجلات", "value": total_records, "indicator": "Blue"},
        {"label": "المعدات", "value": equipment_count, "indicator": "Orange"},
        {"label": "المجموعات", "value": group_count, "indicator": "Purple"},
    ]
    
    # إضافة عدد الفنيين فقط إذا كانت بيانات الفنيين معروضة
    if technicians:
        summary.insert(1, {"label": "عدد الفنيين", "value": len(technicians), "indicator": "Green"})
    
    return summary


def get_chart(data):
    if not data:
        return None

    # Chart data by repair type
    equipment_count = len([d for d in data if d.repair_type == "معدة"])
    group_count = len([d for d in data if d.repair_type == "مجموعة"])

    chart = {
        "data": {
            "labels": ["المعدات", "المجموعات"],
            "datasets": [
                {
                    "name": "التوزيع حسب النوع",
                    "values": [equipment_count, group_count]
                }
            ]
        },
        "type": "pie",
        "height": 300,
        "title": "توزيع الإصلاحات حسب النوع"
    }

    return chart





import frappe
from frappe import _
from frappe.utils import getdate

def execute(filters=None):
    """
    تقرير البطاريات الرئيسي
    """
    columns = get_columns()
    data = get_batteries_data(filters)
    chart = get_batteries_chart(data)
    report_summary = get_batteries_summary(data)
    
    return columns, data, None, chart, report_summary

def get_columns():
    """إعداد أعمدة التقرير"""
    return [
        {
            "fieldname": "item_code",
            "label": _("باركود"),
            "fieldtype": "Link",
            "options": "Army Item Batteries",

            "width": 150
        },
        {
            "fieldname": "item_name",
            "label": _("اسم الصنف"),
            "fieldtype": "Link",
            "options": "Army Item Batteries",
            "width": 200
        },
       
        {
            "fieldname": "capacity",
            "label": _("السعة"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "qty",
            "label": _("الكمية"),
            "fieldtype": "Int",
            "width": 120,

        },
        {
            "fieldname": "manufacture_date",
            "label": _("تاريخ الإنتاج"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "xx_number",
            "label": _("الرقم التسلسلي"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "status",
            "label": _("الحالة"),
            "fieldtype": "Data", 
            "width": 80
        }
   
    ]

def get_batteries_data(filters):
    """جلب بيانات البطاريات مع الفلاتر"""
    conditions = []
    values = {}
    
    # فلتر كود المنتج
    if filters.get("item_code"):
        conditions.append("item_code = %(item_code)s")
        values["item_code"] = filters.get("item_code")
    
    # فلتر اسم المنتج
    if filters.get("item_name"):
        conditions.append("item_name LIKE %(item_name)s")
        values["item_name"] = f"%{filters.get('item_name')}%"
    
    # فلتر تصنيف المنتج
    if filters.get("item_group"):
        conditions.append("item_group = %(item_group)s")
        values["item_group"] = filters.get("item_group")
    
    # فلتر السعة
    if filters.get("capacity"):
        conditions.append("capacity = %(capacity)s")
        values["capacity"] = filters.get("capacity")
    
    # فلتر الرقم التسلسلي
    if filters.get("xx_number"):
        conditions.append("xx_number LIKE %(xx_number)s")
        values["xx_number"] = f"%{filters.get('xx_number')}%"
    
    # فلتر المستودع
    if filters.get("warehouse"):
        conditions.append("warehouse = %(warehouse)s")
        values["warehouse"] = filters.get("warehouse")
    
    # فلتر الحالة
    status_filter = filters.get("status")
    if status_filter:
        if status_filter == "متوفر":
            conditions.append("qty >= 3")
        elif status_filter == "منخفض":
            conditions.append("qty > 0 AND qty < 3")
        elif status_filter == "نافذ":
            conditions.append("qty = 0")
    
    # فلتر تاريخ الإنتاج
    if filters.get("from_date"):
        conditions.append("manufacture_date >= %(from_date)s")
        values["from_date"] = filters.get("from_date")
    
    if filters.get("to_date"):
        conditions.append("manufacture_date <= %(to_date)s")
        values["to_date"] = filters.get("to_date")
    
    # بناء الاستعلام
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    query = f"""
        SELECT 
            item_code,
            item_name,
            item_group,
            capacity,
            qty,
            manufacture_date,
            xx_number,

            CASE 
                WHEN qty = 0 THEN 'نافذ'
                WHEN qty < 3 THEN 'منخفض' 
                ELSE 'متوفر'
            END as status
        FROM `tabArmy Item Batteries`
        WHERE {where_clause}
        ORDER BY 
            item_group, 
            capacity,
            qty DESC,
            manufacture_date DESC
    """
    
    try:
        return frappe.db.sql(query, values, as_dict=1)
    except Exception as e:
        frappe.log_error(f"Error in batteries report: {str(e)}")
        frappe.throw(_("حدث خطأ في جلب البيانات. يرجى مراجعة السجلات للتفاصيل."))

def get_batteries_chart(data):
    """إنشاء رسم بياني لتوزيع البطاريات حسب السعة"""
    if not data:
        return None
    
    # تجميع البيانات حسب السعة مع معالجة القيم الفارغة
    capacity_data = {}
    for item in data:
        capacity_key = item.get("capacity") or "غير محدد"
        capacity_data[capacity_key] = capacity_data.get(capacity_key, 0) + (item.get("qty") or 0)
    
    if not capacity_data:
        return None
    
    return {
        "data": {
            "labels": list(capacity_data.keys()),
            "datasets": [
                {
                    "name": "الكمية حسب السعة",
                    "values": list(capacity_data.values()),
                    "chartType": "bar"
                }
            ]
        },
        "type": "bar",
        "height": 300,
        "title": "توزيع البطاريات حسب السعة",
        "colors": ["#2E86AB"]
    }

def get_batteries_summary(data):
    """إنشاء ملخص التقرير"""
    if not data:
        return []
    
    # حساب الإحصائيات
    total_qty = sum((item.get("qty") or 0) for item in data)
    total_items = len(data)
    
    out_of_stock = len([item for item in data if item.get("status") == "نافذ"])
    low_stock = len([item for item in data if item.get("status") == "منخفض"])
    in_stock = len([item for item in data if item.get("status") == "متوفر"])
    
    # حساب السعات المختلفة
    capacities = len(set(item.get("capacity") for item in data if item.get("capacity")))
    
    # حساب نسبة التوفير
    availability_rate = (in_stock / total_items * 100) if total_items > 0 else 0
    
    return [
        {
            "value": total_items,
            "label": "إجمالي الأصناف",
            "datatype": "Int",
            "color": "blue"
        },
        {
            "value": total_qty,
            "label": "إجمالي الكمية", 
            "datatype": "Int",
            "color": "green"
        },
        {
            "value": f"{capacities}",
            "label": "أنواع السعات",
            "datatype": "Int",
            "color": "purple"
        },
        {
            "value": in_stock,
            "label": "أصناف متوفرة",
            "datatype": "Int",
            "color": "green"
        },
        {
            "value": low_stock,
            "label": "أصناف منخفضة",
            "datatype": "Int", 
            "color": "orange"
        },
        {
            "value": f"{availability_rate:.1f}%",
            "label": "معدل التوفير",
            "datatype": "Percent",
            "color": "light-blue"
        }
    ]

def get_filter_conditions(filters, field, value_key=None, operator="=", use_like=False):
    """دالة مساعدة لإنشاء شروط الفلتر"""
    value = filters.get(field)
    if not value:
        return None, None
    
    field_key = value_key or field
    if use_like:
        return f"{field} LIKE %({field_key})s", {field_key: f"%{value}%"}
    else:
        return f"{field} {operator} %({field_key})s", {field_key: value}

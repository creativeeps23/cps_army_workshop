import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_tires_data(filters)
    chart = get_tires_chart(data)
    report_summary = get_tires_summary(data)
    
    return columns, data, None, chart, report_summary

def get_columns():
    return [
        {
            "fieldname": "item_code",
            "label": _("كود المنتج"),
            "fieldtype": "Link",
            "options": "Army Item Tires",
            "width": 120
        },
        {
            "fieldname": "item_name",
            "label": _("اسم المنتج"), 
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "item_group",
            "label": _("الماركة"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "النوع",
            "label": _("النوع"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "المقاس",
            "label": _("المقاس"),
            "fieldtype": "Data",
            "width": 80
        },
        {
            "fieldname": "qty",
            "label": _("الكمية"),
            "fieldtype": "Float",
            "width": 80,
            "precision": 0
        },
        {
            "fieldname": "تاريخ_الإنتاج",
            "label": _("تاريخ الإنتاج"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "status",
            "label": _("الحالة"),
            "fieldtype": "Data",
            "width": 80
        }
    ]

def get_tires_data(filters):
    conditions = []
    values = {}
    
    if filters.get("item_code"):
        conditions.append("item_code LIKE %(item_code)s")
        values["item_code"] = f"%{filters.get('item_code')}%"
    
    if filters.get("item_name"):
        conditions.append("item_name LIKE %(item_name)s")
        values["item_name"] = f"%{filters.get('item_name')}%"
    
    if filters.get("item_group"):
        conditions.append("item_group = %(item_group)s")
        values["item_group"] = filters.get("item_group")
    
    if filters.get("النوع"):
        conditions.append("النوع = %(نوع)s")
        values["نوع"] = filters.get("النوع")
    
    if filters.get("المقاس"):
        conditions.append("المقاس = %(مقاس)s")
        values["مقاس"] = filters.get("المقاس")
    
    if filters.get("status"):
        if filters.get("status") == "متوفر":
            conditions.append("qty >= 5")
        elif filters.get("status") == "منخفض":
            conditions.append("qty > 0 AND qty < 5")
        elif filters.get("status") == "نافذ":
            conditions.append("qty = 0")
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    query = f"""
        SELECT 
            item_code,
            item_name,
            item_group,
            النوع,
            المقاس,
            qty,
            تاريخ_الإنتاج,
            CASE 
                WHEN qty = 0 THEN 'نافذ'
                WHEN qty < 5 THEN 'منخفض' 
                ELSE 'متوفر'
            END as status
        FROM `tabArmy Item Tires`
        WHERE {where_clause}
        ORDER BY item_group, النوع, المقاس, qty DESC
    """
    
    return frappe.db.sql(query, values, as_dict=1)

def get_tires_chart(data):
    if not data:
        return None
    
    # تجميع حسب النوع
    type_data = {}
    for item in data:
        type_key = item.get("النوع") or "غير محدد"
        if type_key not in type_data:
            type_data[type_key] = 0
        type_data[type_key] += item.get("qty", 0)
    
    # تجميع حسب المقاس
    size_data = {}
    for item in data:
        size_key = item.get("المقاس") or "غير محدد"
        if size_key not in size_data:
            size_data[size_key] = 0
        size_data[size_key] += item.get("qty", 0)
    
    return {
        "data": {
            "labels": list(type_data.keys()),
            "datasets": [
                {
                    "name": "الكمية حسب النوع",
                    "values": list(type_data.values())
                }
            ]
        },
        "type": "pie",
        "height": 300,
        "title": "توزيع الكاوتش حسب النوع"
    }

def get_tires_summary(data):
    if not data:
        return []
    
    total_qty = sum(item.get("qty", 0) for item in data)
    total_items = len(data)
    
    out_of_stock = len([item for item in data if item.get("status") == "نافذ"])
    low_stock = len([item for item in data if item.get("status") == "منخفض"])
    in_stock = len([item for item in data if item.get("status") == "متوفر"])
    
    # أنواع مختلفة
    types = len(set(item.get("النوع") for item in data if item.get("النوع")))
    sizes = len(set(item.get("المقاس") for item in data if item.get("المقاس")))
    
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
            "datatype": "Float",
            "color": "green"
        },
        {
            "value": f"{types} نوع / {sizes} مقاس",
            "label": "الأنواع والمقاسات",
            "datatype": "Data",
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
        }
    ]

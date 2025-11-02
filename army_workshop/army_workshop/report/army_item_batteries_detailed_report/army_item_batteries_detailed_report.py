import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_batteries_data(filters)
    chart = get_batteries_chart(data)
    report_summary = get_batteries_summary(data)
    
    return columns, data, None, chart, report_summary

def get_columns():
    return [
        {
            "fieldname": "item_code",
            "label": _("كود المنتج"),
            "fieldtype": "Link", 
            "options": "Item",
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
            "label": _("تصنيف المنتج"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "capacity",
            "label": _("السعة"),
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
            "fieldname": "manufacture_date",
            "label": _("تاريخ الإنتاج"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "xx_number",
            "label": _("XX Number"),
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
    
    if filters.get("capacity"):
        conditions.append("capacity = %(capacity)s")
        values["capacity"] = filters.get("capacity")
    
    if filters.get("xx_number"):
        conditions.append("xx_number LIKE %(xx_number)s")
        values["xx_number"] = f"%{filters.get('xx_number')}%"
    
    if filters.get("status"):
        if filters.get("status") == "متوفر":
            conditions.append("qty >= 3")
        elif filters.get("status") == "منخفض":
            conditions.append("qty > 0 AND qty < 3")
        elif filters.get("status") == "نافذ":
            conditions.append("qty = 0")
    
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
        ORDER BY item_group, capacity, qty DESC
    """
    
    return frappe.db.sql(query, values, as_dict=1)

def get_batteries_chart(data):
    if not data:
        return None
    
    # تجميع حسب السعة
    capacity_data = {}
    for item in data:
        capacity_key = item.get("capacity") or "غير محدد"
        if capacity_key not in capacity_data:
            capacity_data[capacity_key] = 0
        capacity_data[capacity_key] += item.get("qty", 0)
    
    return {
        "data": {
            "labels": list(capacity_data.keys()),
            "datasets": [
                {
                    "name": "الكمية حسب السعة",
                    "values": list(capacity_data.values())
                }
            ]
        },
        "type": "bar",
        "height": 300,
        "title": "توزيع البطاريات حسب السعة"
    }

def get_batteries_summary(data):
    if not data:
        return []
    
    total_qty = sum(item.get("qty", 0) for item in data)
    total_items = len(data)
    
    out_of_stock = len([item for item in data if item.get("status") == "نافذ"])
    low_stock = len([item for item in data if item.get("status") == "منخفض"])
    in_stock = len([item for item in data if item.get("status") == "متوفر"])
    
    # سعات مختلفة
    capacities = len(set(item.get("capacity") for item in data if item.get("capacity")))
    
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
            "value": f"{capacities} سعة مختلفة",
            "label": "الأنواع",
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

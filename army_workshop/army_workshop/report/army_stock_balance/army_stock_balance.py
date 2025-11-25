import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_detailed_data(filters)
    chart = get_detailed_chart(data)
    report_summary = get_detailed_summary(data)
    
    return columns, data, None, chart, report_summary

def get_columns():
    return [
        {
            "fieldname": "category",
            "label": _("الفئة"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "item_type", 
            "label": _("النوع"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "size_capacity",
            "label": _("المقاس/السعة"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "brand",
            "label": _("الماركة"),
            "fieldtype": "Data", 
            "width": 120
        },
        {
            "fieldname": "item_code",
            "label": _("كود الصنف"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "part_number",
            "label": _("رقم القطعة"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "current_qty",
            "label": _("الكمية"),
            "fieldtype": "Int",
            "width": 80,
            "precision": 0
        },
        {
            "fieldname": "total_value",
            "label": _("الإجمالي"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "details",
            "label": _("تفاصيل إضافية"),
            "fieldtype": "Data",
            "width": 150
        }
    ]

def get_detailed_data(filters=None):
    data = []
    
    # جلب بيانات الكاوتش بشكل مفصل
    tires_data = get_detailed_tires()
    data.extend(tires_data)
    
    # جلب بيانات البطاريات بشكل مفصل
    batteries_data = get_detailed_batteries()
    data.extend(batteries_data)
    
    # جلب بيانات الفلاتر بشكل مفصل
    filters_data = get_detailed_filters()
    data.extend(filters_data)
    
    # جلب بيانات قطع الغيار بشكل مفصل
    workshop_data = get_detailed_workshop_items()
    data.extend(workshop_data)
    
    # تطبيق الفلاتر
    if filters:
        if filters.get("category"):
            data = [d for d in data if d.get("category") == filters.get("category")]
        if filters.get("item_type"):
            data = [d for d in data if filters.get("item_type").lower() in d.get("item_type", "").lower()]
        if filters.get("size_capacity"):
            data = [d for d in data if filters.get("size_capacity").lower() in d.get("size_capacity", "").lower()]
    
    return data

def get_detailed_tires():
    """جلب بيانات الكاوتش بشكل مفصل مع التجميع"""
    tires_summary = frappe.db.sql("""
        SELECT 
            النوع as item_type,
            المقاس as size_capacity,
            item_group as brand,
            COUNT(*) as variants_count,
            SUM(qty) as total_qty
        FROM `tabArmy Item Tires`
        WHERE qty > 0
        GROUP BY النوع, المقاس, item_group
        HAVING total_qty > 0
        ORDER BY total_qty DESC, النوع, المقاس
    """, as_dict=1)
    
    detailed_tires = []
    for tire in tires_summary:
        # جلب أمثلة للأكواد الموجودة
        sample_items = frappe.db.sql("""
            SELECT item_code, qty 
            FROM `tabArmy Item Tires`
            WHERE النوع = %s AND المقاس = %s AND item_group = %s AND qty > 0
            LIMIT 3
        """, (tire.item_type, tire.size_capacity, tire.brand), as_dict=1)
        
        item_codes = ", ".join([f"{item.item_code} ({item.qty})" for item in sample_items])
        if tire.variants_count > 3:
            item_codes += f" + {tire.variants_count - 3} أكثر"
        
        detailed_tires.append({
            "category": "كاوتش",
            "item_type": tire.item_type or "غير محدد",
            "size_capacity": tire.size_capacity or "غير محدد",
            "brand": tire.brand or "غير محدد",
            "item_code": f"{tire.variants_count} نوع",
            "part_number": "-",
            "current_qty": tire.total_qty,
            "total_value": f"{tire.total_qty} وحدة",
            "details": item_codes
        })
    
    return detailed_tires

def get_detailed_batteries():
    """جلب بيانات البطاريات بشكل مفصل مع التجميع"""
    batteries_summary = frappe.db.sql("""
        SELECT 
            item_name as item_type,
            capacity as size_capacity,
            item_group as brand,
            COUNT(*) as variants_count,
            SUM(qty) as total_qty
        FROM `tabArmy Item Batteries`
        WHERE qty > 0
        GROUP BY item_name, capacity, item_group
        HAVING total_qty > 0
        ORDER BY total_qty DESC, item_name, capacity
    """, as_dict=1)
    
    detailed_batteries = []
    for battery in batteries_summary:
        # جلب أمثلة للأكواد الموجودة
        sample_items = frappe.db.sql("""
            SELECT item_code, qty, xx_number
            FROM `tabArmy Item Batteries`
            WHERE item_name = %s AND capacity = %s AND item_group = %s AND qty > 0
            LIMIT 3
        """, (battery.item_type, battery.size_capacity, battery.brand), as_dict=1)
        
        item_details = ", ".join([f"{item.item_code} ({item.qty})" for item in sample_items])
        if battery.variants_count > 3:
            item_details += f" + {battery.variants_count - 3} أكثر"
        
        detailed_batteries.append({
            "category": "بطاريات",
            "item_type": battery.item_type or "غير محدد",
            "size_capacity": battery.size_capacity or "غير محدد",
            "brand": battery.brand or "غير محدد",
            "item_code": f"{battery.variants_count} نوع",
            "part_number": "-",
            "current_qty": battery.total_qty,
            "total_value": f"{battery.total_qty} وحدة",
            "details": item_details
        })
    
    return detailed_batteries

def get_detailed_filters():
    """جلب بيانات الفلاتر بشكل مفصل مع التجميع"""
    filters_summary = frappe.db.sql("""
        SELECT 
            النوع as item_type,
            item_name,
            item_group as brand,
            COUNT(*) as variants_count,
            SUM(qty) as total_qty
        FROM `tabArmy Stock Filters`
        WHERE qty > 0
        GROUP BY النوع, item_name, item_group
        HAVING total_qty > 0
        ORDER BY total_qty DESC, النوع, item_name
    """, as_dict=1)
    
    detailed_filters = []
    for filter_item in filters_summary:
        # جلب أمثلة للأكواد الموجودة
        sample_items = frappe.db.sql("""
            SELECT item_code, qty, part_number
            FROM `tabArmy Stock Filters`
            WHERE النوع = %s AND item_name = %s AND item_group = %s AND qty > 0
            LIMIT 3
        """, (filter_item.item_type, filter_item.item_name, filter_item.brand), as_dict=1)
        
        part_numbers = []
        for item in sample_items:
            if item.part_number:
                part_numbers.append(item.part_number)
        
        part_info = ", ".join(part_numbers) if part_numbers else "غير محدد"
        if filter_item.variants_count > 3:
            part_info += f" + {filter_item.variants_count - 3} أكثر"
        
        detailed_filters.append({
            "category": "فلاتر",
            "item_type": filter_item.item_type or "غير محدد",
            "size_capacity": filter_item.item_name or "غير محدد",
            "brand": filter_item.brand or "غير محدد",
            "item_code": f"{filter_item.variants_count} نوع",
            "part_number": part_info,
            "current_qty": filter_item.total_qty,
            "total_value": f"{filter_item.total_qty} وحدة",
            "details": f"{filter_item.variants_count} موديل"
        })
    
    return detailed_filters

def get_detailed_workshop_items():
    """جلب بيانات قطع الغيار بشكل مفصل مع التجميع"""
    workshop_summary = frappe.db.sql("""
        SELECT 
            item_name as item_type,
            item_group as brand,
            COUNT(*) as variants_count,
            SUM(qty) as total_qty
        FROM `tabArmy Workshop Items`
        WHERE qty > 0
        GROUP BY item_name, item_group
        HAVING total_qty > 0
        ORDER BY total_qty DESC, item_name
    """, as_dict=1)
    
    detailed_workshop = []
    for workshop_item in workshop_summary:
        # جلب أمثلة للأكواد الموجودة
        sample_items = frappe.db.sql("""
            SELECT item_code, qty, part_number
            FROM `tabArmy Workshop Items`
            WHERE item_name = %s AND item_group = %s AND qty > 0
            LIMIT 3
        """, (workshop_item.item_type, workshop_item.brand), as_dict=1)
        
        part_numbers = []
        for item in sample_items:
            if item.part_number:
                part_numbers.append(item.part_number)
        
        part_info = ", ".join(part_numbers) if part_numbers else "غير محدد"
        if workshop_item.variants_count > 3:
            part_info += f" + {workshop_item.variants_count - 3} أكثر"
        
        detailed_workshop.append({
            "category": "قطع غيار",
            "item_type": workshop_item.item_type or "غير محدد",
            "size_capacity": "-",
            "brand": workshop_item.brand or "غير محدد",
            "item_code": f"{workshop_item.variants_count} نوع",
            "part_number": part_info,
            "current_qty": workshop_item.total_qty,
            "total_value": f"{workshop_item.total_qty} وحدة",
            "details": f"{workshop_item.variants_count} موديل"
        })
    
    return detailed_workshop

def get_detailed_chart(data):
    """رسم بياني تفصيلي"""
    if not data:
        return None
    
    # تجميع البيانات حسب النوع والمقاس
    type_size_data = {}
    for item in data:
        key = f"{item.get('item_type')} - {item.get('size_capacity')}"
        if key not in type_size_data:
            type_size_data[key] = 0
        type_size_data[key] += item.get("current_qty", 0)
    
    # أخذ أعلى 10 عناصر فقط للوضوح
    sorted_items = sorted(type_size_data.items(), key=lambda x: x[1], reverse=True)[:10]
    
    labels = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]
    
    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "الكمية حسب النوع والمقاس",
                    "values": values
                }
            ]
        },
        "type": "bar",
        "height": 400,
        "colors": ["#7CD6FD"]
    }

def get_detailed_summary(data):
    """ملخص تفصيلي للتقرير"""
    if not data:
        return []
    
    total_categories = len(set(item.get("category") for item in data))
    total_types = len(set(f"{item.get('category')}-{item.get('item_type')}" for item in data))
    total_qty = sum(item.get("current_qty", 0) for item in data)
    
    # تجميع حسب الفئة
    category_summary = {}
    for item in data:
        category = item.get("category")
        if category not in category_summary:
            category_summary[category] = 0
        category_summary[category] += item.get("current_qty", 0)
    
    category_info = ", ".join([f"{k}: {v}" for k, v in category_summary.items()])
    
    return [
        {
            "value": total_categories,
            "label": "عدد الفئات",
            "datatype": "Int",
            "color": "blue"
        },
        {
            "value": total_types,
            "label": "عدد الأنواع",
            "datatype": "Int",
            "color": "green"
        },
        {
            "value": total_qty,
            "label": "إجمالي الكمية",
            "datatype": "Int",
            "color": "orange"
        },
        {
            "value": category_info,
            "label": "التوزيع",
            "datatype": "Data",
            "color": "purple"
        }
    ]

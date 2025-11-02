import frappe
from frappe.model.document import Document

class ArmyStockEntry(Document):
    def validate(self):
        self.validate_required_fields()
    
    def on_submit(self):
        self.update_all_stock_quantities("increase")
        frappe.msgprint("✅ تم تحديث المخزون بنجاح!")
    
    def on_cancel(self):
        self.update_all_stock_quantities("decrease")
        frappe.msgprint("✅ تم التراجع عن العملية!")
    
    def validate_required_fields(self):
        if self.category == "كاوتش" and not self.tires:
            frappe.throw("⚠️ يرجى إضافة أصناف الكاوتش في الجدول")
        elif self.category == "بطاريات" and not self.batteries:
            frappe.throw("⚠️ يرجى إضافة أصناف البطاريات في الجدول")
        elif self.category == "فلاتر" and not self.filters:
            frappe.throw("⚠️ يرجى إضافة أصناف الفلاتر في الجدول")
        elif self.category in ["قطع غيار", "المتداول"] and not self.workshop_items:
            frappe.throw("⚠️ يرجى إضافة أصناف قطع الغيار في الجدول")
    
    def update_all_stock_quantities(self, action):
        multiplier = 1 if action == "increase" else -1
        
        if self.category == "كاوتش":
            self.update_tires_stock(multiplier)
        elif self.category == "بطاريات":
            self.update_batteries_stock(multiplier)
        elif self.category == "فلاتر":
            self.update_filters_stock(multiplier)
        elif self.category in ["قطع غيار", "المتداول"]:
            self.update_workshop_stock(multiplier)
    
    def update_tires_stock(self, multiplier):
        for tire in self.tires:
            if not tire.item_code or not tire.qty:
                continue
            self.create_or_update_tire(tire, multiplier)
    
    def update_batteries_stock(self, multiplier):
        for battery in self.batteries:
            if not battery.item_code or not battery.qty:
                continue
            self.create_or_update_battery(battery, multiplier)
    
    def update_filters_stock(self, multiplier):
        for filter_item in self.filters:
            if not filter_item.item_code or not filter_item.qty:
                continue
            self.create_or_update_filter(filter_item, multiplier)
    
    def update_workshop_stock(self, multiplier):
        for workshop_item in self.workshop_items:
            if not workshop_item.item_code or not workshop_item.qty:
                continue
            self.create_or_update_workshop_item(workshop_item, multiplier)
    
    def create_or_update_tire(self, tire, multiplier):
        try:
            filters = {'item_code': tire.item_code}
            if tire.المقاس:
                filters['المقاس'] = tire.المقاس
            if tire.النوع:
                filters['النوع'] = tire.النوع
            
            existing_tire = frappe.db.exists("Army Item Tires", filters)
            
            if existing_tire:
                doc = frappe.get_doc("Army Item Tires", existing_tire)
                doc.qty = doc.qty + (multiplier * tire.qty)
                doc.save(ignore_permissions=True)
                frappe.db.commit()
            else:
                new_tire = frappe.new_doc("Army Item Tires")
                new_tire.update({
                    "item_code": tire.item_code,
                    "item_group": tire.item_group or "كاوتش",
                    "item_name": tire.item_name or tire.item_code,
                    "qty": multiplier * tire.qty,
                    "النوع": tire.النوع,
                    "المقاس": tire.المقاس,
                    "تاريخ_الإنتاج": tire.تاريخ_الإنتاج
                })
                new_tire.insert(ignore_permissions=True)
                frappe.db.commit()
                
        except Exception as e:
            frappe.msgprint(f"❌ خطأ في {tire.item_code}: {str(e)}")
    
    def create_or_update_battery(self, battery, multiplier):
        try:
            filters = {'item_code': battery.item_code}
            if hasattr(battery, 'capacity') and battery.capacity:
                filters['capacity'] = battery.capacity
            if hasattr(battery, 'xx_number') and battery.xx_number:
                filters['xx_number'] = battery.xx_number
            
            existing_battery = frappe.db.exists("Army Item Batteries", filters)
            
            if existing_battery:
                doc = frappe.get_doc("Army Item Batteries", existing_battery)
                doc.qty = doc.qty + (multiplier * battery.qty)
                doc.save(ignore_permissions=True)
                frappe.db.commit()
            else:
                new_battery = frappe.new_doc("Army Item Batteries")
                new_battery.item_code = battery.item_code
                new_battery.item_name = battery.item_name or battery.item_code
                new_battery.item_group = getattr(battery, 'item_group', 'بطاريات')
                new_battery.qty = multiplier * battery.qty
                
                if hasattr(battery, 'capacity'):
                    new_battery.capacity = battery.capacity
                if hasattr(battery, 'manufacture_date'):
                    new_battery.manufacture_date = battery.manufacture_date
                if hasattr(battery, 'xx_number'):
                    new_battery.xx_number = battery.xx_number
                
                new_battery.insert(ignore_permissions=True)
                frappe.db.commit()
                
        except Exception as e:
            frappe.msgprint(f"❌ خطأ في {battery.item_code}: {str(e)}")
    
    def create_or_update_filter(self, filter_item, multiplier):
        try:
            filters = {'item_code': filter_item.item_code}
            if hasattr(filter_item, 'part_number') and filter_item.part_number:
                filters['part_number'] = filter_item.part_number
            if hasattr(filter_item, 'xx_number') and filter_item.xx_number:
                filters['xx_number'] = filter_item.xx_number
            
            existing_filter = frappe.db.exists("Army Stock Filters", filters)
            
            if existing_filter:
                doc = frappe.get_doc("Army Stock Filters", existing_filter)
                doc.qty = doc.qty + (multiplier * filter_item.qty)
                doc.save(ignore_permissions=True)
                frappe.db.commit()
            else:
                new_filter = frappe.new_doc("Army Stock Filters")
                new_filter.update({
                    "item_code": filter_item.item_code,
                    "item_group": getattr(filter_item, 'item_group', 'فلاتر'),
                    "xx_number": getattr(filter_item, 'xx_number', ''),
                    "النوع": getattr(filter_item, 'النوع', ''),
                    "item_name": filter_item.item_name or filter_item.item_code,
                    "qty": multiplier * filter_item.qty,
                    "part_number": getattr(filter_item, 'part_number', '')
                })
                new_filter.insert(ignore_permissions=True)
                frappe.db.commit()
                
        except Exception as e:
            frappe.msgprint(f"❌ خطأ في {filter_item.item_code}: {str(e)}")
    
    def create_or_update_workshop_item(self, workshop_item, multiplier):
        try:
            filters = {'item_code': workshop_item.item_code}
            if hasattr(workshop_item, 'part_number') and workshop_item.part_number:
                filters['part_number'] = workshop_item.part_number
            if hasattr(workshop_item, 'xx_number') and workshop_item.xx_number:
                filters['xx_number'] = workshop_item.xx_number
            
            existing_item = frappe.db.exists("Army Workshop Items", filters)
            
            if existing_item:
                doc = frappe.get_doc("Army Workshop Items", existing_item)
                doc.qty = doc.qty + (multiplier * workshop_item.qty)
                doc.save(ignore_permissions=True)
                frappe.db.commit()
            else:
                new_item = frappe.new_doc("Army Workshop Items")
                new_item.update({
                    "item_code": workshop_item.item_code,
                    "item_name": workshop_item.item_name or workshop_item.item_code,
                    "item_group": getattr(workshop_item, 'item_group', 'قطع غيار'),
                    "qty": multiplier * workshop_item.qty,
                    "xx_number": getattr(workshop_item, 'xx_number', ''),
                    "part_number": getattr(workshop_item, 'part_number', '')
                })
                new_item.insert(ignore_permissions=True)
                frappe.db.commit()
                
        except Exception as e:
            frappe.msgprint(f"❌ خطأ في {workshop_item.item_code}: {str(e)}")

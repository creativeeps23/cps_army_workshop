import frappe
from frappe.model.document import Document

class ArmyItemTires(Document):
    def before_insert(self):
        """
        Generate item_code before document is inserted
        """
        if not self.item_code:
            self.item_code = self.generate_serial_number()
    
    def generate_serial_number(self):
        """
        Generate serial number in format TR-0001, TR-0002, etc.
        """
        try:
            last_item = frappe.db.sql("""
                SELECT item_code 
                FROM `tabArmy Item Tires` 
                WHERE item_code LIKE 'TR-%%' 
                ORDER BY creation DESC 
                LIMIT 1
            """)
            
            if last_item and last_item[0][0]:
                last_number = int(last_item[0][0].split('-')[1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            return f"TR-{new_number:04d}"
            
        except Exception:
            return "TR-0001"

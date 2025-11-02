import frappe
from frappe.model.document import Document

class ArmyStockFilters(Document):
    def before_save(self):
        """
        Generate automatic item_code starting with FR- followed by serial number
        """
        if not self.item_code:
            self.item_code = self.generate_serial_number()
    
    def validate(self):
        """
        Validate and ensure item_code is generated
        """
        if not self.item_code:
            self.item_code = self.generate_serial_number()
    
    def generate_serial_number(self):
        """
        Generate serial number in format FR-0001, FR-0002, etc.
        """
        # Get the last item_code from database
        last_item = frappe.db.sql("""
            SELECT item_code 
            FROM `tabArmy Stock Filters` 
            WHERE item_code LIKE 'FR-%' 
            ORDER BY creation DESC 
            LIMIT 1
        """)
        
        if last_item and last_item[0][0]:
            # Extract number from last item_code and increment
            last_number = int(last_item[0][0].split('-')[1])
            new_number = last_number + 1
        else:
            # Start from 1 if no items exist
            new_number = 1
        
        # Format as FR-0001, FR-0002, etc.
        return f"FR-{new_number:04d}"

import frappe
import io
import base64
import barcode
from barcode.writer import ImageWriter


def _generate_png_bytes(code):
    """Return PNG bytes for given code using python-barcode + Pillow"""
    CODE128 = barcode.get_barcode_class('code128')
    buffer = io.BytesIO()

    # ⚙️ إعدادات لتوليد الشريط بدون كتابة تحته
    CODE128(code, writer=ImageWriter()).write(buffer, options={
        "write_text": False,   # 🔹 إخفاء النص التلقائي
        "module_width": 0.3,   # عرض الخطوط
        "module_height": 20,   # ارتفاع الشريط
        "quiet_zone": 3        # مسافة فارغة حول الشريط
    })

    buffer.seek(0)
    return buffer.read()


@frappe.whitelist()
def create_and_attach_barcode(doctype, docname):
    """
    Generate barcode PNG, save as File (public), attach to document field `barcode_image`.
    Returns the file_url.
    """
    doc = frappe.get_doc(doctype, docname)

    try:
        png_bytes = _generate_png_bytes(doc.name)
    except Exception as e:
        frappe.log_error(f"Barcode generation error: {e}", "barcode")
        frappe.throw(f"Barcode generation error: {e}")

    file_name = f"{docname}_barcode.png"

    # إنشاء ملف جديد وربطه بالمستند
    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": file_name,
        "is_private": 0,
        "attached_to_doctype": doctype,
        "attached_to_name": docname,
        "content": base64.b64encode(png_bytes).decode("utf-8"),
        "decode": True
    })

    try:
        file_doc.insert(ignore_permissions=True)
    except frappe.DuplicateEntryError:
        import uuid
        file_doc.file_name = f"{docname}_barcode_{uuid.uuid4().hex[:6]}.png"
        file_doc.insert(ignore_permissions=True)

    file_url = file_doc.file_url

    try:
        doc.db_set("barcode_image", file_url)
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"Failed to set barcode_image: {e}", "barcode")

    return file_url


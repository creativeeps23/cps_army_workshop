import frappe
import io
import base64
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
import os
import qrcode
from io import BytesIO

def _generate_qr_code_for_thermal_printer(data, size=120):
    """توليد QR Code مناسب للطابعات الحرارية"""
    #⚙️ إعدادات QR Code للطابعات الحرارية
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=3,  # حجم أصغر للطابعات الحرارية
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # إنشاء QR Code
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # تحجيم الصورة
    qr_img = qr_img.resize((size, size), Image.LANCZOS)
    
    return _add_text_below_qr_code(qr_img, data)

def _add_text_below_qr_code(qr_image, text):
    """إضافة النص أسفل QR Code"""
    qr_width, qr_height = qr_image.size
    
    # ⚡ إعدادات النص للطابعات الحرارية
    text_height = 25
    new_height = qr_height + text_height
    
    new_image = Image.new('RGB', (qr_width, new_height), 'white')
    new_image.paste(qr_image, (0, 0))
    
    draw = ImageDraw.Draw(new_image)
    
    try:
        font_path = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"
        if os.path.exists(font_path):
            font = ImageFont.truetype(font_path, 14)
        else:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # حساب وعرض النص
    try:
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
    except AttributeError:
        text_width, text_height_val = draw.textsize(text, font=font)
        text_bbox = (0, 0, text_width, text_height_val)
    
    text_x = (qr_width - text_width) // 2
    text_y = qr_height + 5
    
    draw.text((text_x, text_y), text, fill='black', font=font)
    
    # ✅ حفظ بإعدادات مناسبة للطابعات
    output_buffer = BytesIO()
    new_image.save(output_buffer, format='PNG', dpi=(203, 203))
    output_buffer.seek(0)
    
    return output_buffer.read()

@frappe.whitelist()
def create_and_attach_qr_code(doctype, docname):
    """
    توليد QR Code للطابعات الحرارية
    """
    doc = frappe.get_doc(doctype, docname)
    
    # التحقق إذا كان QR Code موجوداً مسبقاً
    if doc.get('qr_code_image'):
        existing_file = frappe.get_all('File', 
            filters={
                'attached_to_doctype': doctype,
                'attached_to_name': docname,
                'file_name': ['like', '%qrcode%']
            },
            fields=['name', 'file_url']
        )
        if existing_file:
            return existing_file[0]['file_url']
    
    try:
        # يمكنك إضافة بيانات إضافية في QR Code
        qr_data = f"{doc.name}"
        png_bytes = _generate_qr_code_for_thermal_printer(qr_data)
    except Exception as e:
        frappe.log_error(f"خطأ في توليد QR Code: {e}", "qrcode")
        frappe.throw(f"خطأ في توليد QR Code: {e}")

    file_name = f"{docname}_qrcode.png"

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
        existing_file = frappe.get_all('File', 
            filters={
                'attached_to_doctype': doctype,
                'attached_to_name': docname,
                'file_name': file_name
            },
            fields=['name', 'file_url']
        )
        if existing_file:
            file_url = existing_file[0]['file_url']
        else:
            import uuid
            file_doc.file_name = f"{docname}_qrcode_{uuid.uuid4().hex[:6]}.png"
            file_doc.insert(ignore_permissions=True)
            file_url = file_doc.file_url
    else:
        file_url = file_doc.file_url

    try:
        doc.db_set("qr_code_image", file_url)
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"فشل في تعيين حقل QR Code: {e}", "qrcode")

    return file_url

@frappe.whitelist()
def create_and_attach_both_codes(doctype, docname):
    """
    توليد الباركود و QR Code معاً
    """
    barcode_url = create_and_attach_barcode(doctype, docname)
    qrcode_url = create_and_attach_qr_code(doctype, docname)
    
    return {
        'barcode_url': barcode_url,
        'qrcode_url': qrcode_url
    }
    
def _generate_barcode_for_thermal_printer(code):
    """توليد باركود مناسب للطابعات الحرارية"""
    CODE128 = barcode.get_barcode_class('code128')
    buffer = io.BytesIO()
    
    # ⚙️ الإعدادات المثالية للطابعات الحرارية
    barcode_obj = CODE128(code, writer=ImageWriter())
    barcode_obj.write(buffer, options={
        "write_text": False,   # إخفاء النص التلقائي
        "module_width": 0.2,   # عرض الخطوط - أنسب للطابعات الحرارية
        "module_height": 15,   # ارتفاع الشريط - مناسب للقراءة
        "quiet_zone": 2,       # مسافة فارغة أقل لتوفير المساحة
        "font_size": 0,
        "text_distance": 0,
        "dpi": 203            # DPI شائع في الطابعات الحرارية
    })
    
    buffer.seek(0)
    barcode_image = Image.open(buffer)
    
    # تحجيم الصورة لمقاس مناسب للطابعات الحرارية
    target_width = 400  # عرض مناسب لمعظم الطابعات الحرارية
    width_percent = target_width / float(barcode_image.size[0])
    target_height = int(float(barcode_image.size[1]) * float(width_percent))
    
    barcode_image = barcode_image.resize((target_width, target_height), Image.LANCZOS)
    
    return _add_text_below_barcode_thermal(barcode_image, code)

def _add_text_below_barcode_thermal(barcode_image, text):
    """إضافة النص مع إعدادات مناسبة للطابعات الحرارية"""
    barcode_width, barcode_height = barcode_image.size
    
    # ⚡ إعدادات النص للطابعات الحرارية
    text_height = 25  # ارتفاع أقل لتوفير المساحة
    new_height = barcode_height + text_height
    
    new_image = Image.new('RGB', (barcode_width, new_height), 'white')
    new_image.paste(barcode_image, (0, 0))
    
    draw = ImageDraw.Draw(new_image)
    
    try:
        # استخدام خط بسيط وواضح للطابعات الحرارية
        font_path = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"
        if os.path.exists(font_path):
            font = ImageFont.truetype(font_path, 16)  # حجم خط أكبر للوضوح
        else:
            # خط بديل إذا لم يتوفر الخط المطلوب
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # حساب وعرض النص
    try:
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
    except AttributeError:
        # للتوافق مع إصدارات PIL القديمة
        text_width, text_height_val = draw.textsize(text, font=font)
        text_bbox = (0, 0, text_width, text_height_val)
    
    text_x = (barcode_width - text_width) // 2
    text_y = barcode_height + 2  # مسافة صغيرة بين الباركود والنص
    
    # كتابة النص باللون الأسود (أفضل للطابعات الحرارية)
    draw.text((text_x, text_y), text, fill='black', font=font)
    
    # ✅ حفظ بإعدادات مناسبة للطابعات
    output_buffer = io.BytesIO()
    new_image.save(output_buffer, format='PNG', dpi=(203, 203))
    output_buffer.seek(0)
    
    return output_buffer.read()

@frappe.whitelist()
def create_and_attach_barcode(doctype, docname):
    """
    توليد الباركود للطابعات الحرارية
    """
    doc = frappe.get_doc(doctype, docname)
    
    # التحقق إذا كان الباركود موجوداً مسبقاً
    if doc.get('barcode_image'):
        existing_file = frappe.get_all('File', 
            filters={
                'attached_to_doctype': doctype,
                'attached_to_name': docname,
                'file_name': ['like', '%barcode%']
            },
            fields=['name', 'file_url']
        )
        if existing_file:
            return existing_file[0]['file_url']
    
    try:
        png_bytes = _generate_barcode_for_thermal_printer(doc.name)
    except Exception as e:
        frappe.log_error(f"خطأ في توليد الباركود: {e}", "barcode")
        frappe.throw(f"خطأ في توليد الباركود: {e}")

    file_name = f"{docname}_barcode.png"

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
        existing_file = frappe.get_all('File', 
            filters={
                'attached_to_doctype': doctype,
                'attached_to_name': docname,
                'file_name': file_name
            },
            fields=['name', 'file_url']
        )
        if existing_file:
            file_url = existing_file[0]['file_url']
        else:
            import uuid
            file_doc.file_name = f"{docname}_barcode_{uuid.uuid4().hex[:6]}.png"
            file_doc.insert(ignore_permissions=True)
            file_url = file_doc.file_url
    else:
        file_url = file_doc.file_url

    try:
        doc.db_set("barcode_image", file_url)
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"فشل في تعيين حقل الباركود: {e}", "barcode")

    return file_url
// Copyright (c) 2025, Creative Programming Solutions and contributors
// For license information, please see license.txt

frappe.ui.form.on('Army Workshop Items', {
	// refresh: function(frm) {


    refresh: function(frm) {
        // إضافة زر لتوليد الباركود يدوياً إذا لم يكن موجوداً
        if (!frm.doc.barcode_image) {
            frm.add_custom_button(__('Generate Barcode'), function() {
                generate_barcode(frm);
            });
        }
    },
    
    after_save: function(frm) {
        // توليد الباركود تلقائياً فقط إذا لم يكن موجوداً
        if (!frm.doc.barcode_image) {
            generate_barcode(frm);
        }
    }
});

function generate_barcode(frm) {
    frappe.call({
            method: "army_workshop.api.barcode_utils.create_and_attach_barcode",
        args: {
            doctype: frm.doc.doctype,
            docname: frm.doc.name
        },
        callback: function(r) {
            if (r.message) {
                frappe.show_alert({
                    message: "✅ تم توليد الباركود بنجاح!", 
                    indicator: 'green'
                });
                frm.reload_doc();
            } else {
                frappe.msgprint("❌ لم يتم توليد الباركود.");
            }
        }
    });
}

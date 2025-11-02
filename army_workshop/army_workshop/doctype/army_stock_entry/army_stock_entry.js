frappe.ui.form.on('Army Stock Entry', {
    refresh: function(frm) {
        toggle_fields(frm);
    },
    category: function(frm) {
        toggle_fields(frm);
    }
});

function toggle_fields(frm) {
    // إخفاء جميع الفيلدات أولاً
    frm.set_df_property('tires', 'hidden', 1);
    frm.set_df_property('batteries', 'hidden', 1);
    frm.set_df_property('filters', 'hidden', 1);
    frm.set_df_property('workshop_items', 'hidden', 1);

    // نجيب القيمة بعد إزالة أي مسافات زائدة
    let cat = (frm.doc.category || '').trim();

    if (cat === 'كاوتش') {
        frm.set_df_property('tires', 'hidden', 0);
    } else if (cat === 'بطاريات') {
        frm.set_df_property('batteries', 'hidden', 0);
    } else if (cat === 'فلاتر') {
        frm.set_df_property('filters', 'hidden', 0);
    } else {
        // في أي حالة أخرى
        frm.set_df_property('workshop_items', 'hidden', 0);
    }
}


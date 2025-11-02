frappe.ui.form.on('Equipment Repair', {
    refresh: function(frm) {
        toggleSections(frm);
        updateFieldRequirements(frm);
        addStatusUpdateButton(frm);
    },

    administration_approval_category: function(frm) {
        toggleSections(frm);
        updateFieldRequirements(frm);
    },
    
    repair_type: function(frm) {
        toggleSections(frm);
        updateFieldRequirements(frm);
    },

    repair_category: function(frm) {
        // إذا كان repair_category = Outside repair والحالة = جار الإصلاح
        if (frm.doc.repair_category === 'مأمورية إصلاح خارجية' && frm.doc.status === 'جار الإصلاح') {
            frm.set_value('status', 'جار الإصلاح - مأمورية');
            frappe.show_alert({
                message: __('تم تحديث الحالة تلقائياً إلى: جار الإصلاح - مأمورية'),
                indicator: 'blue'
            });
        }

        toggleSections(frm);
        updateFieldRequirements(frm);
        frm.refresh(); // لتحديث زر الحالة تلقائياً
    },

    status: function(frm) {
        updateFieldRequirements(frm);
    },

    ex_repair: function(frm) {
        // تحديث الحقول بعد تغيير ex_repair
        frm.refresh_field('ex_repair');
        frappe.after_ajax(() => {
            toggleSections(frm);
            updateFieldRequirements(frm);
            frm.refresh(); 
        });
    },

    // أحداث للحقول لتحديث العرض عند تغيير قيمها
    تاريخ_إنتهاء_الأعمال: function(frm) {
        updateFieldVisibility(frm);
    },

    leave_date: function(frm) {
        updateFieldVisibility(frm);
    },

    // حدث قبل الحفظ للتحقق من الحقول الإلزامية
    before_save: function(frm) {
        validateRequiredFields(frm);
    }
});

function toggleSections(frm) {
    // إخفاء جميع الأقسام أولاً
    const sections = [
        'with_administration_approval_section',
        'without_administration_approval_section', 
        'group_section',
        'team_data',
        'external_repair_tab'
    ];
    
    sections.forEach(section => {
        frm.set_df_property(section, 'hidden', 1);
    });

    // التحكم في أقسام الموافقة الإدارية
    switch(frm.doc.administration_approval_category) {
        case "بتصديق الإدارة":
            frm.set_df_property('with_administration_approval_section', 'hidden', 0);
            break;
        case "بدون تصديق الإدارة":
            frm.set_df_property('without_administration_approval_section', 'hidden', 0);
            break;
    }

    // التحكم في أقسام نوع الإصلاح - إظهار group_section إذا كان repair_type = مجموعة
    if (frm.doc.repair_type === "Part" || frm.doc.repair_type === "مجموعة") {
        frm.set_df_property('group_type', 'hidden', 0);
        frm.set_df_property('group_section', 'hidden', 0);
    }

    // الشرط الجديد: إذا كان repair_category = Outside Repair
    if (frm.doc.repair_category === "مأمورية إصلاح خارجية") {
        frm.set_df_property('team_data', 'hidden', 0);
    }

    // ✅ إظهار external_repair_tab إذا كان ex_repair معلم
    if (cint(frm.doc.ex_repair) === 1) {
        try {
            // إذا كان Tab Break
            frm.get_field('external_repair_tab').tab.hide(false);
        } catch(e) {
            // إذا كان Section Break
            frm.set_df_property('مندوب_الشركة', 'hidden', 0);
            frm.set_df_property('الشركة', 'hidden', 0);
            frm.set_df_property('تاريخ_التسليم_للشركة', 'hidden', 0);
            frm.set_df_property('تاريخ_الإستلام_من_الشركة', 'hidden', 0);
            frm.set_df_property('contact_phone', 'hidden', 0);
        }
    }
}

function updateFieldRequirements(frm) {
    // إعادة تعيين جميع الحقول إلى غير إلزامية أولاً
    const fields = [
        'leave_date',
        'تاريخ_إنتهاء_الأعمال',
        'contact_number',
        'delivery_date_to_company',
        'company_representative',
        'receive_date_from_company'
    ];
    
    fields.forEach(field => {
        frm.set_df_property(field, 'reqd', 0);
    });

    // التحكم في الحقول بناءً على الحالة
    
    // حالة تم التسليم
    if (frm.doc.status === 'تم التسليم') {
        frm.set_df_property('leave_date', 'reqd', 1);
    }

    // حالة تم الإصلاح - جعل تاريخ_إنتهاء_الأعمال إلزامي دائمًا
    if (frm.doc.status === 'تم الإصلاح') {
        frm.set_df_property('تاريخ_إنتهاء_الأعمال', 'reqd', 1);
    }

    // حالة جار الإصلاح -طرف خارجي
    if (frm.doc.status === 'جار الإصلاح -طرف خارجي') {
        frm.set_df_property('contact_number', 'reqd', 1);
        frm.set_df_property('delivery_date_to_company', 'reqd', 1);
        frm.set_df_property('company_representative', 'reqd', 1);
    }

    // حالة تم الإصلاح مع إصلاح خارجي
    if (frm.doc.status === 'تم الإصلاح' && frm.doc.ex_repair) {
        frm.set_df_property('receive_date_from_company', 'reqd', 1);
    }
    
    // تحديث ظهور الحقول بناءً على القيم
    updateFieldVisibility(frm);
}

// دالة جديدة لتحديث ظهور الحقول بناءً على القيم
function updateFieldVisibility(frm) {
    // جعل تاريخ_إنتهاء_الأعمال غير مخفي إذا كان يحتوي على قيمة
    if (frm.doc.تاريخ_إنتهاء_الأعمال) {
        frm.set_df_property('تاريخ_إنتهاء_الأعمال', 'hidden', 0);
    } else {
        frm.set_df_property('تاريخ_إنتهاء_الأعمال', 'hidden', frm.doc.status !== 'تم الإصلاح');
    }

    // جعل leave_date غير مخفي إذا كان يحتوي على قيمة
    if (frm.doc.leave_date) {
        frm.set_df_property('leave_date', 'hidden', 0);
    } else {
        frm.set_df_property('leave_date', 'hidden', frm.doc.status !== 'تم التسليم');
    }

    // الحقول الأخرى نتحكم فيها بالشروط العادية
    frm.set_df_property('contact_number', 'hidden', frm.doc.status !== 'جار الإصلاح -طرف خارجي');
    frm.set_df_property('delivery_date_to_company', 'hidden', frm.doc.status !== 'جار الإصلاح -طرف خارجي');
    frm.set_df_property('company_representative', 'hidden', frm.doc.status !== 'جار الإصلاح -طرف خارجي');
    frm.set_df_property('receive_date_from_company', 'hidden', !(frm.doc.status === 'تم الإصلاح' && frm.doc.ex_repair));
}

// دالة للتحقق من صلاحيات المستخدم
function checkUserPermission(allowedRoles) {
    const userRoles = frappe.user_roles;
    return allowedRoles.some(role => userRoles.includes(role));
}

function addStatusUpdateButton(frm) {
    if (frm.custom_buttons) {
        const buttonsToKeep = [];
        for (let key in frm.custom_buttons) {
            if (frm.custom_buttons.hasOwnProperty(key)) {
                if (!key.includes('تحديث إلى:')) {
                    buttonsToKeep.push(key);
                }
            }
        }
        for (let key in frm.custom_buttons) {
            if (frm.custom_buttons.hasOwnProperty(key) && !buttonsToKeep.includes(key)) {
                delete frm.custom_buttons[key];
            }
        }
    }

    const currentStatus = frm.doc.status;
    let nextStatus = '';
    let allowedRoles = [];

    // تحديد الحالة التالية والصلاحيات المسموح بها
    switch(currentStatus) {
        case 'قيد الفحص':
            if (frm.doc.repair_category === 'مأمورية إصلاح خارجية') {
                nextStatus = 'جار الإصلاح - مأمورية';
            } else {
                nextStatus = 'جار الإصلاح';
            }
            allowedRoles = ['مكتب الإجراءات', 'مكتب الجودة', 'الورشة'];
            break;
        
        case 'جار الإصلاح':
            if (frm.doc.ex_repair) {
                nextStatus = 'جار الإصلاح -طرف خارجي';
            } else if (frm.doc.repair_category === 'مأمورية إصلاح خارجية') {
                nextStatus = 'جار الإصلاح - مأمورية';
            } else {
                nextStatus = 'تم الإصلاح';
            }
            allowedRoles = ['مكتب الإجراءات', 'مكتب الجودة', 'الورشة'];
            break;
        
        case 'جار الإصلاح -طرف خارجي':
        case 'جار الإصلاح - مأمورية':
            nextStatus = 'تم الإصلاح';
            allowedRoles = ['مكتب الإجراءات', 'مكتب الجودة', 'الورشة'];
            break;
        
        case 'تم الإصلاح':
            nextStatus = 'تم الإعتماد من الإجراءات';
            allowedRoles = ['مكتب الإجراءات']; // فقط مكتب الإجراءات
            break;
        
        case 'تم الإعتماد من الإجراءات':
            nextStatus = 'تم التسليم';
            allowedRoles = ['مكتب الإجراءات', 'مكتب الجودة']; // مكتب الإجراءات والجودة
            break;
        
        case 'تم التسليم':
            return; // لا تظهر زر في الحالة النهائية
        
        default:
            if (!currentStatus || currentStatus === '') {
                nextStatus = 'قيد الفحص';
                allowedRoles = ['مكتب الإجراءات', 'مكتب الجودة', 'الورشة'];
            }
    }

    // التحقق من صلاحية المستخدم
    if (nextStatus && checkUserPermission(allowedRoles)) {
        frm.add_custom_button(__('تحديث إلى: ' + nextStatus), function() {
            frm.set_value('status', nextStatus);
            
            if (nextStatus === 'جار الإصلاح -طرف خارجي' && !frm.doc.ex_repair) {
                frm.set_value('ex_repair', 1);
            }
            
            if (nextStatus === 'جار الإصلاح - مأمورية' && frm.doc.repair_category !== 'مأمورية إصلاح خارجية') {
                frm.set_value('repair_category', 'مأمورية إصلاح خارجية');
            }
            
            frm.save();
            frappe.show_alert({
                message: __('تم تحديث الحالة إلى: ') + nextStatus,
                indicator: 'green'
            });
        }, __('تحديث الحالة'));
    }
}

function validateRequiredFields(frm) {
    if (frm.doc.status === 'تم الإصلاح' && !frm.doc.تاريخ_إنتهاء_الأعمال) {
        frappe.throw(__('حقل تاريخ إنتهاء الأعمال إلزامي عندما تكون الحالة "تم الإصلاح". يرجى ملء هذا الحقل أولاً.'));
    }

    if (frm.doc.status === 'تم التسليم' && !frm.doc.leave_date) {
        frappe.throw(__('حقل تاريخ التسليم إلزامي عندما تكون الحالة "تم التسليم". يرجى ملء هذا الحقل أولاً.'));
    }

    if (frm.doc.status === 'جار الإصلاح -طرف خارجي') {
        if (!frm.doc.مندوب_الشركة) {
            frappe.throw(__('حقل مندوب الشركة إلزامي عندما تكون الحالة "جار الإصلاح -طرف خارجي". يرجى ملء هذا الحقل أولاً.'));
        }
        if (!frm.doc.contact_phone) {
            frappe.throw(__('حقل رقم التواصل إلزامي عندما تكون الحالة "جار الإصلاح -طرف خارجي". يرجى ملء هذا الحقل أولاً.'));
        }
        if (!frm.doc.تاريخ_التسليم_للشركة) {
            frappe.throw(__('حقل تاريخ التسليم للشركة إلزامي عندما تكون الحالة "جار الإصلاح -طرف خارجي". يرجى ملء هذا الحقل أولاً.'));
        }
        
    }

    if (frm.doc.status === 'تم الإصلاح' && frm.doc.ex_repair) {
        if (!frm.doc.تاريخ_الإستلام_من_الشركة) {
            frappe.throw(__('حقل تاريخ الإستلام من الشركة إلزامي عندما تكون الحالة "تم الإصلاح" والإصلاح خارجي. يرجى ملء هذا الحقل أولاً.'));
        }
    }
}

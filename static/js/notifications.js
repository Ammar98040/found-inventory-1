// نظام الإشعارات الفورية

// إشعارات قاعدة البيانات
const Notifications = {
    // عرض إشعار جديد
    show: function(type, title, message, duration = 5000) {
        // إنشاء حاوية الإشعارات إن لم تكن موجودة
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            document.body.appendChild(container);
        }
        
        // إنشاء إشعار جديد
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        // الأيقونة حسب النوع
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        
        const icon = icons[type] || 'ℹ️';
        
        // محتوى الإشعار
        notification.innerHTML = `
            <div class="notification-icon">${icon}</div>
            <div class="notification-content">
                <div class="notification-title">${title}</div>
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">×</button>
            <div class="notification-progress ${type}" style="animation-duration: ${duration}ms;"></div>
        `;
        
        // إضافة الإشعار
        container.appendChild(notification);
        
        // إغلاق تلقائي بعد المدة المحددة
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.classList.add('removing');
                    setTimeout(() => {
                        if (notification.parentElement) {
                            notification.remove();
                        }
                    }, 300);
                }
            }, duration);
        }
    },
    
    // إشعار نجاح
    success: function(title, message, duration) {
        this.show('success', title, message, duration);
    },
    
    // إشعار خطأ
    error: function(title, message, duration) {
        this.show('error', title, message, duration);
    },
    
    // إشعار تحذير
    warning: function(title, message, duration) {
        this.show('warning', title, message, duration);
    },
    
    // إشعار معلومات
    info: function(title, message, duration) {
        this.show('info', title, message, duration);
    }
};

// إشعارات المنتجات
const ProductNotifications = {
    // إشعار إضافة منتج
    added: function(productNumber, productName) {
        Notifications.success(
            'تم إضافة المنتج بنجاح',
            `${productNumber} - ${productName}`,
            4000
        );
    },
    
    // إشعار تعديل منتج
    updated: function(productNumber, productName) {
        Notifications.info(
            'تم تعديل المنتج',
            `${productNumber} - ${productName}`,
            4000
        );
    },
    
    // إشعار حذف منتج
    deleted: function(productNumber, productName) {
        Notifications.warning(
            'تم حذف المنتج',
            `${productNumber} - ${productName}`,
            4000
        );
    },
    
    // إشعار تخصيص موقع
    locationAssigned: function(productNumber, location) {
        Notifications.success(
            'تم تخصيص الموقع',
            `${productNumber} → ${location}`,
            4000
        );
    },
    
    // إشعار إزالة موقع
    locationRemoved: function(productNumber) {
        Notifications.info(
            'تم إزالة الموقع',
            `${productNumber}`,
            4000
        );
    },
    
    // إشعار سحب كمية
    quantityTaken: function(productNumber, quantity) {
        Notifications.info(
            'تم سحب الكمية',
            `${productNumber}: -${quantity}`,
            4000
        );
    },
    
    // إشعار إضافة كمية
    quantityAdded: function(productNumber, quantity) {
        Notifications.success(
            'تم إضافة الكمية',
            `${productNumber}: +${quantity}`,
            4000
        );
    },
    
    // إشعار خطأ
    error: function(message) {
        Notifications.error(
            'خطأ في العملية',
            message,
            5000
        );
    }
};

// إشعارات الأماكن
const LocationNotifications = {
    created: function(location) {
        Notifications.success(
            'تم إنشاء الموقع',
            location,
            3000
        );
    },
    
    updated: function(location) {
        Notifications.info(
            'تم تحديث الموقع',
            location,
            3000
        );
    },
    
    deleted: function(location) {
        Notifications.warning(
            'تم حذف الموقع',
            location,
            3000
        );
    }
};

// إشعارات المستودع
const WarehouseNotifications = {
    rowAdded: function(row) {
        Notifications.success(
            'تم إضافة صف',
            `الصف ${row}`,
            3000
        );
    },
    
    columnAdded: function(column) {
        Notifications.success(
            'تم إضافة عمود',
            `العمود ${column}`,
            3000
        );
    },
    
    rowDeleted: function(row) {
        Notifications.warning(
            'تم حذف صف',
            `الصف ${row}`,
            3000
        );
    },
    
    columnDeleted: function(column) {
        Notifications.warning(
            'تم حذف عمود',
            `العمود ${column}`,
            3000
        );
    }
};

// تطبيق الإشعارات تلقائياً على الأزرار والنماذج
document.addEventListener('DOMContentLoaded', function() {
    // مراقبة أزرار الحذف
    document.querySelectorAll('[data-notify-on-delete]').forEach(button => {
        button.addEventListener('click', function() {
            const productNumber = this.getAttribute('data-product-number');
            const productName = this.getAttribute('data-product-name');
            
            setTimeout(() => {
                if (confirm('هل أنت متأكد من الحذف؟')) {
                    ProductNotifications.deleted(productNumber, productName);
                }
            }, 100);
        });
    });
    
    // مراقبة النماذج
    document.querySelectorAll('form[data-notify-on-submit]').forEach(form => {
        form.addEventListener('submit', function(e) {
            const action = this.getAttribute('data-action');
            const formData = new FormData(this);
            const productNumber = formData.get('product_number') || '';
            
            setTimeout(() => {
                if (action === 'add') {
                    ProductNotifications.added(productNumber, '');
                } else if (action === 'update') {
                    ProductNotifications.updated(productNumber, '');
                }
            }, 100);
        });
    });
    
    function checkInventoryInsightsReminder() {
        fetch('/api/get-stats/')
            .then(r => r.json())
            .then(data => {
                const l = data.low_stock_count || 0;
                const r = data.reorder_count || 0;
                const o = data.overstock_count || 0;
                const w = data.watchlist_count || 0;
                if ((l + r + o + w) > 0) {
                    const msg = `إعادة الطلب: ${r} • فائض: ${o} • متابعة: ${w} • منخفض عام: ${l}`;
                    Notifications.warning('توصيات المخزون', msg, 3000);
                    setTimeout(() => {
                        const container = document.getElementById('notification-container');
                        if (container && container.lastElementChild) {
                            const n = container.lastElementChild;
                            n.style.cursor = 'pointer';
                            n.onclick = () => { window.location.href = '/inventory-insights/'; };
                        }
                    }, 50);
                }
            })
            .catch(()=>{});
    }
    
    checkInventoryInsightsReminder();
    setInterval(checkInventoryInsightsReminder, 3600000);
});

// تصدير للاستخدام العالمي
window.Notifications = Notifications;
window.ProductNotifications = ProductNotifications;
window.LocationNotifications = LocationNotifications;
window.WarehouseNotifications = WarehouseNotifications;


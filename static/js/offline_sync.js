/**
 * Offline Sync Manager
 * Handles queuing orders when offline and syncing them when online.
 */

class OfflineManager {
    constructor() {
        this.queueKey = 'inventory_offline_orders';
        this.isOnline = navigator.onLine;
        this.init();
    }

    init() {
        // Listen for online/offline events
        window.addEventListener('online', () => {
            this.updateStatus(true);
            this.syncOrders();
        });
        
        window.addEventListener('offline', () => {
            this.updateStatus(false);
        });

        // Initial status check
        this.updateStatus(this.isOnline);
        
        // Create UI indicator if not exists
        if (!document.getElementById('offline-indicator')) {
            this.createIndicator();
        }
        
        // Update indicator text initially
        this.updateIndicator();
    }

    updateStatus(online) {
        this.isOnline = online;
        this.updateIndicator();
        
        if (online) {
            console.log('App is online. Ready to sync.');
        } else {
            console.log('App is offline. Orders will be queued.');
        }
    }

    createIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'offline-indicator';
        indicator.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 20px;
            padding: 10px 15px;
            border-radius: 8px;
            font-weight: bold;
            z-index: 9999;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            display: none;
        `;
        document.body.appendChild(indicator);
    }

    updateIndicator() {
        const indicator = document.getElementById('offline-indicator');
        if (!indicator) return;

        const queue = this.getQueue();
        const count = queue.length;

        if (!this.isOnline) {
            indicator.style.display = 'block';
            indicator.style.background = '#fee2e2'; // Red-100
            indicator.style.color = '#991b1b'; // Red-800
            indicator.style.border = '1px solid #ef4444';
            indicator.innerHTML = `⚠️ وضع غير متصل (${count} طلبات معلقة)`;
        } else if (count > 0) {
            indicator.style.display = 'block';
            indicator.style.background = '#fef3c7'; // Yellow-100
            indicator.style.color = '#92400e'; // Yellow-800
            indicator.style.border = '1px solid #f59e0b';
            indicator.innerHTML = `⏳ جاري المزامنة... (${count} طلبات)`;
        } else {
            indicator.style.display = 'none';
        }
    }

    getQueue() {
        try {
            return JSON.parse(localStorage.getItem(this.queueKey) || '[]');
        } catch (e) {
            console.error('Error reading offline queue:', e);
            return [];
        }
    }

    saveQueue(queue) {
        try {
            localStorage.setItem(this.queueKey, JSON.stringify(queue));
            this.updateIndicator();
        } catch (e) {
            console.error('Error saving offline queue:', e);
            alert('خطأ: مساحة التخزين ممتلئة، لا يمكن حفظ الطلب!');
        }
    }

    async queueOrder(orderData) {
        const queue = this.getQueue();
        // Add timestamp and unique ID for tracking
        const orderItem = {
            id: Date.now() + Math.random().toString(36).substr(2, 9),
            timestamp: new Date().toISOString(),
            data: orderData,
            attempts: 0
        };
        
        queue.push(orderItem);
        this.saveQueue(queue);
        
        // Show success message for queuing
        alert('📴 لا يوجد اتصال بالإنترنت. تم حفظ الطلب محلياً وسيتم إرساله تلقائياً عند عودة الاتصال.');
        
        return orderItem;
    }

    async syncOrders() {
        const queue = this.getQueue();
        if (queue.length === 0) return;

        console.log(`Syncing ${queue.length} offline orders...`);
        this.updateIndicator();

        const remainingQueue = [];
        let successCount = 0;

        for (const item of queue) {
            try {
                // Try to send the order
                const response = await fetch('/api/confirm-products/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCsrfToken()
                    },
                    body: JSON.stringify(item.data)
                });

                const data = await response.json();

                if (data.success) {
                    successCount++;
                    console.log(`Order ${item.id} synced successfully.`);
                } else {
                    console.error(`Failed to sync order ${item.id}: ${data.error}`);
                    // If it's a server error (not validation), keep it in queue
                    // For validation errors (like insufficient stock), we might need a strategy
                    // For now, we'll keep it if it's not a clear "client error" that won't be fixed by retry
                    // But to avoid infinite loops on bad data, maybe we should move it to a "failed" list
                    // or just log it. 
                    
                    // Simple strategy: if status is 4xx (except 408/429), drop it. 5xx or network error, keep it.
                    if (response.status >= 400 && response.status < 500) {
                         alert(`فشل مزامنة طلب محفوظ: ${data.error}`);
                         // Don't add back to queue (drop it)
                    } else {
                        item.attempts++;
                        remainingQueue.push(item);
                    }
                }
            } catch (error) {
                console.error(`Network error syncing order ${item.id}:`, error);
                item.attempts++;
                remainingQueue.push(item);
            }
        }

        this.saveQueue(remainingQueue);

        if (successCount > 0) {
            const msg = `تمت مزامنة ${successCount} طلبات محفوظة بنجاح!`;
            console.log(msg);
            // Optional: show a toast notification
            const toast = document.createElement('div');
            toast.textContent = msg;
            toast.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: #10b981;
                color: white;
                padding: 15px;
                border-radius: 8px;
                z-index: 10000;
                box-shadow: 0 4px 6px rgba(0,0,0,0.2);
                animation: fadeInOut 3s ease forwards;
            `;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
            
            // Reload if needed to update UI
            if (remainingQueue.length === 0) {
                 // Maybe reload page or update UI if we are on the products page
                 // window.location.reload(); 
            }
        }
    }

    getCsrfToken() {
        const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (tokenInput) return tokenInput.value;
        
        // Fallback: try to get from cookie
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Initialize the manager
const offlineManager = new OfflineManager();

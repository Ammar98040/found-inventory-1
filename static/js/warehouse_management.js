let currentGrid = {
    rows: 6,
    columns: 15,
    grid: {}
};

// تحميل الشبكة عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    refreshGrid();
});

// تحديث الشبكة
async function refreshGrid() {
    showLoading();
    
    try {
        const response = await fetch('/api/grid/');
        const data = await response.json();
        
        currentGrid = data;
        updateGridDisplay();
        updateInfoPanel();
        
    } catch (error) {
        showError('حدث خطأ أثناء تحميل الشبكة: ' + error.message);
    } finally {
        hideLoading();
    }
}

// عرض الشبكة
function updateGridDisplay() {
    const gridContainer = document.getElementById('warehouse-grid');
    gridContainer.innerHTML = '';
    
    // تعيين تنسيق flex مع عرض محدد للخلايا
    gridContainer.style.display = 'flex';
    gridContainer.style.flexDirection = 'column';
    gridContainer.style.gap = '0';
    
    // إنشاء رأس الأعمدة
    const headerRow = document.createElement('div');
    headerRow.style.display = 'flex';
    headerRow.style.gap = '0';
    
    // الخلية الفارغة في الزاوية
    const cornerCell = document.createElement('div');
    cornerCell.className = 'grid-cell grid-cell-header';
    cornerCell.style.width = '50px';
    cornerCell.style.height = '50px';
    headerRow.appendChild(cornerCell);
    
    // رؤوس الأعمدة
    for (let col = 1; col <= currentGrid.columns; col++) {
        const headerCell = document.createElement('div');
        headerCell.className = 'grid-cell grid-cell-header';
        headerCell.style.width = '50px';
        headerCell.style.height = '50px';
        headerCell.style.display = 'flex';
        headerCell.style.flexDirection = 'column';
        headerCell.style.alignItems = 'center';
        headerCell.style.justifyContent = 'center';
        
        const colLabel = document.createElement('span');
        colLabel.textContent = col;
        headerCell.appendChild(colLabel);
        
        // زر الترتيب للعمود (فقط إذا كان هناك صفوف)
        if (currentGrid.rows > 1) {
            const compactBtn = document.createElement('button');
            compactBtn.innerHTML = '⬆️';
            compactBtn.title = 'إعادة ترتيب العمود (ملء الفراغات)';
            compactBtn.style.fontSize = '0.7rem';
            compactBtn.style.border = 'none';
            compactBtn.style.background = 'transparent';
            compactBtn.style.cursor = 'pointer';
            compactBtn.style.padding = '0';
            compactBtn.style.marginTop = '2px';
            compactBtn.onclick = function(e) { 
                e.stopPropagation();
                compactColumn(col); 
            };
            headerCell.appendChild(compactBtn);
        }
        
        headerRow.appendChild(headerCell);
    }
    
    gridContainer.appendChild(headerRow);
    
    // إنشاء الصفوف
    for (let row = 1; row <= currentGrid.rows; row++) {
        const rowDiv = document.createElement('div');
        rowDiv.style.display = 'flex';
        rowDiv.style.gap = '0';
        
        // رأس الصف
        const rowHeader = document.createElement('div');
        rowHeader.className = 'grid-cell grid-cell-header';
        rowHeader.style.width = '50px';
        rowHeader.style.height = '50px';
        rowHeader.style.display = 'flex';
        rowHeader.style.flexDirection = 'column';
        rowHeader.style.alignItems = 'center';
        rowHeader.style.justifyContent = 'center';
        
        const rowLabel = document.createElement('span');
        rowLabel.textContent = row;
        rowHeader.appendChild(rowLabel);
        
        // زر الترتيب (فقط إذا كان هناك أعمدة)
        if (currentGrid.columns > 1) {
            const compactBtn = document.createElement('button');
            compactBtn.innerHTML = '⬅️';
            compactBtn.title = 'إعادة ترتيب الصف (ملء الفراغات)';
            compactBtn.style.fontSize = '0.7rem';
            compactBtn.style.border = 'none';
            compactBtn.style.background = 'transparent';
            compactBtn.style.cursor = 'pointer';
            compactBtn.style.padding = '0';
            compactBtn.style.marginTop = '2px';
            compactBtn.onclick = function(e) { 
                e.stopPropagation();
                compactRow(row); 
            };
            rowHeader.appendChild(compactBtn);
        }
        
        rowDiv.appendChild(rowHeader);
        
        // الخلايا
        for (let col = 1; col <= currentGrid.columns; col++) {
            const cell = document.createElement('div');
            const key = `${row},${col}`;
            const cellData = currentGrid.grid[key] || {};
            
            cell.className = 'grid-cell';
            cell.style.width = '50px';
            cell.style.height = '50px';
            
            if (cellData.has_products) {
                cell.classList.add('has-products');
                // تصميم محسّن للموقع مع منتج (حجم صغير)
                cell.innerHTML = '<div style="padding: 2px; text-align: center; line-height: 1.2;">' + 
                                '<div style="font-size: 0.5rem; font-weight: bold; color: #059669;">R' + row + 'C' + col + '</div>' +
                                '<div style="font-size: 0.45rem; color: #065f46;">' + (cellData.products && cellData.products.length > 0 ? cellData.products[0].substring(0, 6) : '') + '</div>' +
                                '</div>';
            } else {
                // تصميم واضح للموقع الفارغ
                cell.classList.add('empty');
                cell.innerHTML = '<div style="font-size: 0.6rem; font-weight: bold; color: #94a3b8; text-align: center;">R' + row + 'C' + col + '</div>';
            }
            
            // معلومات عند التحويم
            cell.title = `الموقع: R${row}C${col}${cellData.notes ? '\nملاحظات: ' + cellData.notes : ''}${cellData.has_products && cellData.products ? '\nمنتج: ' + cellData.products.join(', ') : '\nموقع فارغ'}`;
            
            rowDiv.appendChild(cell);
        }
        
        gridContainer.appendChild(rowDiv);
    }
}

// تحديث لوحة المعلومات
function updateInfoPanel() {
    const rows = currentGrid.rows;
    const columns = currentGrid.columns;
    
    document.getElementById('rows-count').textContent = rows;
    document.getElementById('columns-count').textContent = columns;
    
    // حساب إجمالي المواقع
    const totalCells = rows * columns;
    document.getElementById('total-cells').textContent = totalCells;
}

// إضافة صف/صفوف متعددة
async function addRowsBulk() {
    console.log('addRowsBulk called');
    const input = document.getElementById('rows-count-input');
    if (!input) {
        console.error('rows-count-input not found');
        alert('لم يتم العثور على حقل إدخال عدد الصفوف');
        return;
    }
    
    const count = parseInt(input.value) || 1;
    console.log('count:', count);
    
    if (count < 1 || count > 50) {
        alert('العدد يجب أن يكون بين 1 و 50');
        return;
    }
    
    if (!confirm(`هل تريد إضافة ${count} صف؟`)) return;
    
    console.log('Starting to add rows...');
    showLoading();
    
    try {
        const response = await fetch('/api/add-row/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ count: count })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`تم إضافة ${data.rows_added} صف بنجاح!\nالعدد الجديد للصفوف: ${data.new_rows_count}`);
            refreshGrid();
        } else {
            throw new Error(data.error || 'حدث خطأ');
        }
        
    } catch (error) {
        showError('حدث خطأ أثناء إضافة الصفوف: ' + error.message);
    } finally {
        hideLoading();
    }
}

// إضافة عمود/أعمدة متعددة
async function addColumnsBulk() {
    const input = document.getElementById('columns-count-input');
    if (!input) {
        alert('لم يتم العثور على حقل إدخال عدد الأعمدة');
        return;
    }
    
    const count = parseInt(input.value) || 1;
    
    if (count < 1 || count > 50) {
        alert('العدد يجب أن يكون بين 1 و 50');
        return;
    }
    
    if (!confirm(`هل تريد إضافة ${count} عمود؟`)) return;
    
    showLoading();
    
    try {
        const response = await fetch('/api/add-column/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ count: count })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`تم إضافة ${data.columns_added} عمود بنجاح!\nالعدد الجديد للأعمدة: ${data.new_columns_count}`);
            refreshGrid();
        } else {
            throw new Error(data.error || 'حدث خطأ');
        }
        
    } catch (error) {
        showError('حدث خطأ أثناء إضافة الأعمدة: ' + error.message);
    } finally {
        hideLoading();
    }
}

// للتوافق مع الكود القديم
async function addRow() {
    addRowsBulk();
}

async function addColumn() {
    addColumnsBulk();
}

// حذف صف/صفوف متعددة
async function deleteRowsBulk() {
    const input = document.getElementById('rows-delete-input');
    if (!input) {
        alert('لم يتم العثور على حقل إدخال عدد الصفوف');
        return;
    }
    
    const count = parseInt(input.value) || 1;
    
    if (count < 1) {
        alert('العدد يجب أن يكون أكبر من 0');
        return;
    }
    
    if (!confirm(`هل تريد حذف ${count} صف؟ سيتم حذف جميع المنتجات في هذه الصفوف!`)) return;
    
    showLoading();
    
    try {
        const response = await fetch('/api/delete-row/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ count: count })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`تم حذف ${data.rows_deleted} صف بنجاح!\nالعدد الجديد للصفوف: ${data.new_rows_count}`);
            refreshGrid();
        } else {
            throw new Error(data.error || 'حدث خطأ');
        }
        
    } catch (error) {
        showError('حدث خطأ أثناء حذف الصفوف: ' + error.message);
    } finally {
        hideLoading();
    }
}

// حذف عمود/أعمدة متعددة
async function deleteColumnsBulk() {
    const input = document.getElementById('columns-delete-input');
    if (!input) {
        alert('لم يتم العثور على حقل إدخال عدد الأعمدة');
        return;
    }
    
    const count = parseInt(input.value) || 1;
    
    if (count < 1) {
        alert('العدد يجب أن يكون أكبر من 0');
        return;
    }
    
    if (!confirm(`هل تريد حذف ${count} عمود؟ سيتم حذف جميع المنتجات في هذه الأعمدة!`)) return;
    
    showLoading();
    
    try {
        const response = await fetch('/api/delete-column/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ count: count })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`تم حذف ${data.columns_deleted} عمود بنجاح!\nالعدد الجديد للأعمدة: ${data.new_columns_count}`);
            refreshGrid();
        } else {
            throw new Error(data.error || 'حدث خطأ');
        }
        
    } catch (error) {
        showError('حدث خطأ أثناء حذف الأعمدة: ' + error.message);
    } finally {
        hideLoading();
    }
}

// للتوافق مع الكود القديم
async function deleteLastRow() {
    deleteRowsBulk();
}

async function deleteLastColumn() {
    deleteColumnsBulk();
}

// إخفاء/إظهار العناصر
function showLoading() {
    const loadingEl = document.getElementById('loading');
    if (loadingEl) {
        loadingEl.style.display = 'block';
    }
}

function hideLoading() {
    const loadingEl = document.getElementById('loading');
    if (loadingEl) {
        loadingEl.style.display = 'none';
    }
}

function showError(message) {
    const errorEl = document.getElementById('error-message');
    if (errorEl) {
        errorEl.textContent = message;
        errorEl.style.display = 'block';
        
        setTimeout(() => {
            errorEl.style.display = 'none';
        }, 5000);
    } else {
        console.error('Error message element not found:', message);
    }
}

function hideError() {
    const errorEl = document.getElementById('error-message');
    if (errorEl) {
        errorEl.style.display = 'none';
    }
}

// إعادة ترتيب الصف
async function compactRow(rowNumber) {
    if (!confirm(`هل أنت متأكد من إعادة ترتيب الصف ${rowNumber}؟\nسيتم نقل المنتجات لملء الفراغات من اليمين إلى اليسار (باتجاه العمود 1).`)) {
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/api/compact-row/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                row: rowNumber
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            await refreshGrid();
            
            // إظهار رسالة النجاح مع زر التراجع
            if (data.can_undo) {
                showUndoNotification(data.message || 'تم إعادة الترتيب بنجاح');
            } else {
                alert(data.message || 'تم إعادة الترتيب بنجاح');
            }
        } else {
            showError(data.error || 'حدث خطأ أثناء إعادة الترتيب');
        }
        
    } catch (error) {
        showError('حدث خطأ: ' + error.message);
    } finally {
        hideLoading();
    }
}

// إعادة ترتيب العمود
async function compactColumn(colNumber) {
    if (!confirm(`هل أنت متأكد من إعادة ترتيب العمود ${colNumber}؟\nسيتم نقل المنتجات لملء الفراغات من الأعلى إلى الأسفل (باتجاه الصف 1).`)) {
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/api/compact-column/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                column: colNumber
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            await refreshGrid();
            
            // إظهار رسالة النجاح مع زر التراجع
            if (data.can_undo) {
                showUndoNotification(data.message || 'تم إعادة الترتيب بنجاح');
            } else {
                alert(data.message || 'تم إعادة الترتيب بنجاح');
            }
        } else {
            showError(data.error || 'حدث خطأ أثناء إعادة الترتيب');
        }
        
    } catch (error) {
        showError('حدث خطأ: ' + error.message);
    } finally {
        hideLoading();
    }
}

// التراجع عن آخر عملية
async function revertCompaction() {
    showLoading();
    
    try {
        const response = await fetch('/api/revert-compaction/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            await refreshGrid();
            alert(data.message || 'تم التراجع بنجاح');
            
            // إخفاء إشعار التراجع
            const undoEl = document.getElementById('undo-notification');
            if (undoEl) undoEl.style.display = 'none';
        } else {
            showError(data.error || 'حدث خطأ أثناء التراجع');
        }
        
    } catch (error) {
        showError('حدث خطأ: ' + error.message);
    } finally {
        hideLoading();
    }
}

// عرض إشعار التراجع
function showUndoNotification(message) {
    let undoEl = document.getElementById('undo-notification');
    
    if (!undoEl) {
        undoEl = document.createElement('div');
        undoEl.id = 'undo-notification';
        undoEl.style.position = 'fixed';
        undoEl.style.bottom = '20px';
        undoEl.style.left = '50%';
        undoEl.style.transform = 'translateX(-50%)';
        undoEl.style.backgroundColor = '#333';
        undoEl.style.color = 'white';
        undoEl.style.padding = '15px 25px';
        undoEl.style.borderRadius = '8px';
        undoEl.style.zIndex = '1000';
        undoEl.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
        undoEl.style.display = 'flex';
        undoEl.style.alignItems = 'center';
        undoEl.style.gap = '15px';
        
        document.body.appendChild(undoEl);
    }
    
    undoEl.innerHTML = `
        <span>${message}</span>
        <button onclick="revertCompaction()" style="background: #ef4444; color: white; border: none; padding: 5px 15px; border-radius: 4px; cursor: pointer; font-weight: bold;">تراجع ↩️</button>
        <button onclick="document.getElementById('undo-notification').style.display='none'" style="background: transparent; color: #aaa; border: none; font-size: 1.2rem; cursor: pointer; margin-right: 5px;">&times;</button>
    `;
    
    undoEl.style.display = 'flex';
    
    // إخفاء تلقائي بعد 10 ثواني
    setTimeout(() => {
        if (undoEl.style.display !== 'none') {
            undoEl.style.display = 'none';
        }
    }, 10000);
}


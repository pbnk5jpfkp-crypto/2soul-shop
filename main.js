// ==================== Utility Functions ====================

/**
 * Show notification toast
 */
function showNotification(message, type = 'success', duration = 3000) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        ${message}
        <button class="close-alert">×</button>
    `;
    
    const container = document.querySelector('.main-content') || document.body;
    container.insertBefore(alert, container.firstChild);
    
    const closeBtn = alert.querySelector('.close-alert');
    closeBtn.onclick = () => alert.remove();
    
    setTimeout(() => {
        if (alert.parentElement) {
            alert.remove();
        }
    }, duration);
}

/**
 * Update cart count in navbar
 */
function updateCartCount() {
    fetch('/api/cart')
        .then(response => response.json())
        .then(data => {
            const count = data.items.length;
            const badge = document.getElementById('cart-count');
            if (badge) {
                badge.textContent = count;
            }
        });
}

/**
 * Format price
 */
function formatPrice(price) {
    return new Intl.NumberFormat('ru-RU').format(price);
}

// ==================== Page Initialization ====================

document.addEventListener('DOMContentLoaded', function() {
    // Update cart count on page load
    updateCartCount();
    
    // Initialize animations
    initializeAnimations();
});

/**
 * Initialize scroll animations
 */
function initializeAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.product-card, .update-card, .stat-card').forEach(el => {
        observer.observe(el);
    });
}

// ==================== Cart Functions ====================

/**
 * Add to cart handler (used in catalog)
 */
async function addToCart(productId) {
    const qty = parseInt(document.getElementById('qty-input').value);
    const sizeBtn = document.querySelector('.size-btn.active');
    const size = sizeBtn ? sizeBtn.dataset.size : 'One Size';
    
    try {
        const response = await fetch('/api/cart/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                product_id: productId,
                quantity: qty,
                size: size
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('✓ Товар добавлен в корзину!', 'success');
            updateCartCount();
            closeProductModal();
        } else {
            showNotification('✗ Ошибка: ' + data.message, 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('✗ Произошла ошибка', 'danger');
    }
}

/**
 * Remove from cart
 */
async function removeFromCart(index) {
    if (!confirm('Удалить товар из корзины?')) return;
    
    try {
        const response = await fetch('/api/cart/remove', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ index: index })
        });
        
        const data = await response.json();
        if (data.success) {
            location.reload();
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('✗ Ошибка при удалении товара', 'danger');
    }
}

// ==================== Modal Functions ====================

/**
 * Close product modal
 */
function closeProductModal() {
    const modal = document.getElementById('product-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// ==================== Admin Functions ====================

/**
 * Switch admin tabs
 */
function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    const tab = document.getElementById(tabName);
    if (tab) {
        tab.classList.add('active');
    }
    event.target.classList.add('active');
    
    // Load products if needed
    if (tabName === 'products') {
        loadProducts();
    }
}

/**
 * Load products for admin
 */
async function loadProducts() {
    try {
        const response = await fetch('/api/admin/products');
        const data = await response.json();
        
        const container = document.getElementById('products-list');
        if (!container) return;
        
        container.innerHTML = data.products.map(p => `
            <div class="order-detail">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4>${p.name}</h4>
                        <p>${p.category} | ₽${formatPrice(p.price)}</p>
                        <p>В наличии: ${p.stock}</p>
                    </div>
                    <div>
                        <button class="btn-small" onclick="editProduct(${p.id})">Редактировать</button>
                        <button class="btn-small btn-danger" onclick="deleteProduct(${p.id})">Удалить</button>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading products:', error);
    }
}

/**
 * Delete product (admin)
 */
async function deleteProduct(productId) {
    if (!confirm('Удалить товар?')) return;
    
    try {
        const response = await fetch(`/api/admin/products/${productId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        if (data.success) {
            showNotification('✓ Товар удалён', 'success');
            loadProducts();
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('✗ Ошибка при удалении товара', 'danger');
    }
}

/**
 * View order details (admin)
 */
async function viewOrderDetail(orderId) {
    try {
        const response = await fetch(`/api/admin/orders/${orderId}`);
        const data = await response.json();
        const order = data.order;
        
        const html = `
            <h2>Заказ #${order.order_number}</h2>
            
            <div class="order-detail">
                <h4>Информация о клиенте</h4>
                <p><strong>Имя:</strong> ${order.customer_name}</p>
                <p><strong>Email:</strong> ${order.customer_email}</p>
                <p><strong>Телефон:</strong> ${order.customer_phone || 'Не указан'}</p>
                <p><strong>Адрес:</strong> ${order.customer_address || 'Не указан'}</p>
            </div>
            
            <div class="order-detail">
                <h4>Товары</h4>
                <ul class="order-items-list">
                    ${order.items.map(item => `
                        <li>
                            ${item.product_name} (${item.size}) ×${item.quantity} = ₽${formatPrice(item.price * item.quantity)}
                        </li>
                    `).join('')}
                </ul>
            </div>
            
            <div class="order-detail">
                <h4>Итого: ₽${formatPrice(order.total_amount)}</h4>
                
                <label style="display: block; margin-bottom: 10px; font-weight: 600;">Статус заказа:</label>
                <select id="order-status" class="form-control" style="margin-bottom: 15px;">
                    <option value="new" ${order.status === 'new' ? 'selected' : ''}>Новый</option>
                    <option value="processing" ${order.status === 'processing' ? 'selected' : ''}>В обработке</option>
                    <option value="completed" ${order.status === 'completed' ? 'selected' : ''}>Выполнен</option>
                    <option value="cancelled" ${order.status === 'cancelled' ? 'selected' : ''}>Отменён</option>
                </select>
                
                <button class="btn btn-primary" onclick="updateOrderStatus(${order.id})">
                    Сохранить
                </button>
            </div>
        `;
        
        document.getElementById('order-detail-content').innerHTML = html;
        document.getElementById('order-modal').style.display = 'flex';
    } catch (error) {
        console.error('Error:', error);
        showNotification('✗ Ошибка при загрузке заказа', 'danger');
    }
}

/**
 * Update order status (admin)
 */
async function updateOrderStatus(orderId) {
    const status = document.getElementById('order-status').value;
    
    try {
        const response = await fetch(`/api/admin/orders/${orderId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: status })
        });
        
        const data = await response.json();
        if (data.success) {
            showNotification('✓ Статус обновлён', 'success');
            closeOrderModal();
            setTimeout(() => location.reload(), 1000);
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('✗ Ошибка при обновлении статуса', 'danger');
    }
}

/**
 * Close order modal
 */
function closeOrderModal() {
    const modal = document.getElementById('order-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Close modals when clicking outside
window.onclick = function(event) {
    const productModal = document.getElementById('product-modal');
    const orderModal = document.getElementById('order-modal');
    
    if (productModal && event.target === productModal) {
        productModal.style.display = 'none';
    }
    
    if (orderModal && event.target === orderModal) {
        orderModal.style.display = 'none';
    }
}

// ==================== Notification Function ====================

/**
 * Show notification toast
 */
function showNotification(message, type = 'success', duration = 3000) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        z-index: 3000;
        min-width: 300px;
        animation: slideInRight 0.3s;
    `;
    alert.innerHTML = `
        ${message}
        <button class="close-alert" style="position: absolute; right: 10px; background: none; border: none; color: inherit; cursor: pointer; font-size: 18px;">×</button>
    `;
    
    document.body.appendChild(alert);
    
    const closeBtn = alert.querySelector('.close-alert');
    closeBtn.onclick = () => {
        alert.style.animation = 'slideOutRight 0.3s';
        setTimeout(() => alert.remove(), 300);
    };
    
    setTimeout(() => {
        if (alert.parentElement) {
            alert.style.animation = 'slideOutRight 0.3s';
            setTimeout(() => alert.remove(), 300);
        }
    }, duration);
}

// Add animations to style
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
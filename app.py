import os
import json
import uuid
from datetime import datetime
from functools import wraps
from dotenv import load_dotenv

from flask import (
    Flask, render_template, request, jsonify, session, redirect, url_for, flash
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

from config import config
from models import db, Product, Order, Admin
from forms import AdminLoginForm

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config.get(os.getenv('FLASK_ENV', 'development')))

print(f"✓ Flask initialized with config: {os.getenv('FLASK_ENV', 'development')}")
print(f"✓ Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'
login_manager.login_message = 'Пожалуйста, войдите в систему'
login_manager.login_message_category = 'warning'

try:
    import yookassa
    yookassa.Configuration.configure(
        app.config.get('YOOKASSA_SHOP_ID', ''),
        app.config.get('YOOKASSA_SECRET_KEY', '')
    )
    print("✓ YooKassa configured")
except Exception as e:
    print(f"⚠ YooKassa configuration error: {e}")

@login_manager.user_loader
def load_user(admin_id):
    """Load user from database."""
    return Admin.query.get(int(admin_id))

# ==================== Database Initialization ====================

def init_db():
    """Initialize database with sample data."""
    with app.app_context():
        print("📦 Initializing database...")
        db.create_all()
        
        # Check if data already exists
        product_count = Product.query.count()
        if product_count > 0:
            print(f"✓ Database already has {product_count} products")
            return
        
        print("📝 Adding sample products...")
        
        # Sample products
        products = [
            Product(
                name="Minimalist T-Shirt",
                description="Классическая минималистическая футболка из 100% хлопка. Идеальна для повседневного стиля. Мягкий материал, удобный крой, подходит для любого сезона.",
                price=2990,
                category="Одежда",
                image_url="https://via.placeholder.com/400x500?text=Minimalist+T-Shirt",
                stock=50
            ),
            Product(
                name="Premium Hoodie",
                description="Удобный худи с мягкой подкладкой. Идеален для прохладной погоды. Практичные карманы, регулируемый капюшон, современный дизайн.",
                price=4990,
                category="Одежда",
                image_url="https://via.placeholder.com/400x500?text=Premium+Hoodie",
                stock=30
            ),
            Product(
                name="Classic Denim",
                description="Высококачественные джинсы классического кроя. Подходят для любого случая. Прочный материал, удобная посадка, вневременной стиль.",
                price=5990,
                category="Одежда",
                image_url="https://via.placeholder.com/400x500?text=Classic+Denim",
                stock=25
            ),
            Product(
                name="Premium Sneakers",
                description="Удобные кроссовки для повседневного использования. Легкие и стильные. Амортизация для комфорта, дышащий материал, спортивный дизайн.",
                price=7990,
                category="Обувь",
                image_url="https://via.placeholder.com/400x500?text=Premium+Sneakers",
                stock=20
            ),
            Product(
                name="Leather Belt",
                description="Кожаный ремень премиум качества. Классический дизайн на любой случай. Натуральная кожа, надежная пряжка, универсальный чёрный цвет.",
                price=2490,
                category="Аксессуары",
                image_url="https://via.placeholder.com/400x500?text=Leather+Belt",
                stock=40
            ),
            Product(
                name="Wool Cap",
                description="Шерстяная шапка премиум качества. Теплая и стильная. Изготовлена из чистой шерсти, защищает от холода, минималистичный дизайн.",
                price=1990,
                category="Аксессуары",
                image_url="https://via.placeholder.com/400x500?text=Wool+Cap",
                stock=35
            ),
            Product(
                name="Silk Scarf",
                description="Элегантный шёлковый шарф. Добавляет изысканность к любому образу. Натуральный шелк, мягкий материал, универсальный дизайн.",
                price=3490,
                category="Аксессуары",
                image_url="https://via.placeholder.com/400x500?text=Silk+Scarf",
                stock=20
            ),
            Product(
                name="Designer Glasses",
                description="Стильные очки в современном дизайне. Защита от УФ-лучей. Качественные линзы, стильная оправа, защита 100% UV.",
                price=8990,
                category="Аксессуары",
                image_url="https://via.placeholder.com/400x500?text=Designer+Glasses",
                stock=15
            ),
        ]
        
        for product in products:
            product.set_sizes(['XS', 'S', 'M', 'L', 'XL', 'XXL'])
            db.session.add(product)
            print(f"  ✓ Added: {product.name}")
        
        # Create admin user
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        existing_admin = Admin.query.filter_by(username=admin_username).first()
        if not existing_admin:
            admin = Admin(
                username=admin_username,
                password=generate_password_hash(admin_password)
            )
            db.session.add(admin)
            print(f"  ✓ Created admin user: {admin_username}")
        
        db.session.commit()
        print(f"✓ Database initialized successfully with {len(products)} products")

# Create tables and init DB
with app.app_context():
    db.create_all()
    init_db()

# ==================== Request Handlers ====================

@app.before_request
def before_request():
    """Before each request."""
    if 'cart' not in session:
        session['cart'] = []

# ==================== Front-end Routes ====================

@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')

@app.route('/catalog')
def catalog():
    """Catalog page."""
    return render_template('catalog.html')

@app.route('/cart')
def cart():
    """Cart page."""
    return render_template('cart.html')

@app.route('/checkout')
def checkout():
    """Checkout page."""
    cart_items = session.get('cart', [])
    if not cart_items:
        flash('Корзина пуста', 'warning')
        return redirect(url_for('catalog'))
    return render_template('checkout.html')

# ==================== API Routes ====================

@app.route('/api/products', methods=['GET'])
def api_products():
    """Get all products."""
    try:
        limit = request.args.get('limit', 0, type=int)
        query = Product.query
        
        if limit > 0:
            query = query.limit(limit)
        
        products = query.all()
        print(f"API /api/products - returning {len(products)} products")
        
        return jsonify({
            'success': True,
            'products': [p.to_dict() for p in products]
        })
    except Exception as e:
        print(f"ERROR in /api/products: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'products': []
        }), 500

@app.route('/api/categories', methods=['GET'])
def api_categories():
    """Get unique product categories."""
    try:
        categories = db.session.query(Product.category).distinct().all()
        cats = [cat[0] for cat in categories if cat[0]]
        print(f"API /api/categories - returning {len(cats)} categories: {cats}")
        
        return jsonify({
            'success': True,
            'categories': cats
        })
    except Exception as e:
        print(f"ERROR in /api/categories: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'categories': []
        }), 500

@app.route('/api/cart', methods=['GET'])
def api_get_cart():
    """Get cart contents."""
    cart = session.get('cart', [])
    
    enriched_cart = []
    for item in cart:
        product = Product.query.get(item['product_id'])
        if product:
            enriched_cart.append({
                'product_id': product.id,
                'name': product.name,
                'price': product.price,
                'image_url': product.image_url,
                'quantity': item['quantity'],
                'size': item['size']
            })
    
    return jsonify({'success': True, 'items': enriched_cart})

@app.route('/api/cart/add', methods=['POST'])
def api_add_to_cart():
    """Add item to cart."""
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    size = data.get('size', 'One Size')
    
    if not session.get('cart'):
        session['cart'] = []
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'success': False, 'message': 'Товар не найден'}), 404
    
    cart = session['cart']
    found = False
    for item in cart:
        if item['product_id'] == product_id and item['size'] == size:
            item['quantity'] += quantity
            found = True
            break
    
    if not found:
        cart.append({
            'product_id': product_id,
            'quantity': quantity,
            'size': size
        })
    
    session.modified = True
    return jsonify({'success': True, 'message': 'Товар добавлен'})

@app.route('/api/cart/remove', methods=['POST'])
def api_remove_from_cart():
    """Remove item from cart."""
    data = request.get_json()
    index = data.get('index')
    
    cart = session.get('cart', [])
    if 0 <= index < len(cart):
        cart.pop(index)
        session.modified = True
    
    return jsonify({'success': True})

@app.route('/api/cart/update', methods=['POST'])
def api_update_cart():
    """Update cart item quantity."""
    data = request.get_json()
    index = data.get('index')
    delta = data.get('delta', 0)
    
    cart = session.get('cart', [])
    if 0 <= index < len(cart):
        cart[index]['quantity'] += delta
        if cart[index]['quantity'] <= 0:
            cart.pop(index)
        session.modified = True
    
    return jsonify({'success': True})

@app.route('/api/checkout', methods=['POST'])
def api_checkout():
    """Create order from cart."""
    data = request.get_json()
    cart = session.get('cart', [])
    
    if not cart:
        return jsonify({'success': False, 'message': 'Корзина пуста'}), 400
    
    order_items = []
    total_amount = 0
    
    for item in cart:
        product = Product.query.get(item['product_id'])
        if product:
            item_total = product.price * item['quantity']
            total_amount += item_total
            order_items.append({
                'product_id': product.id,
                'product_name': product.name,
                'price': product.price,
                'quantity': item['quantity'],
                'size': item['size']
            })
    
    order_number = f"2S-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    order = Order(
        order_number=order_number,
        customer_name=data.get('customer_name'),
        customer_email=data.get('customer_email'),
        customer_phone=data.get('customer_phone'),
        customer_address=data.get('customer_address'),
        notes=data.get('notes'),
        total_amount=total_amount,
        status=Order.STATUS_NEW
    )
    
    order.set_items(order_items)
    db.session.add(order)
    db.session.commit()
    
    session['cart'] = []
    session.modified = True
    
    return jsonify({
        'success': True,
        'order_id': order.id,
        'order_number': order.order_number
    })

# ==================== Payment Routes ====================

@app.route('/payment/<int:order_id>')
def payment_page(order_id):
    """Payment page."""
    order = Order.query.get_or_404(order_id)
    return render_template('payment.html', order=order)

@app.route('/api/create-payment', methods=['POST'])
def api_create_payment():
    """Create payment through YooKassa."""
    data = request.get_json()
    order_id = data.get('order_id')
    
    order = Order.query.get_or_404(order_id)
    
    try:
        import yookassa
        payment = yookassa.Payment.create({
            "amount": {
                "value": f"{order.total_amount:.2f}",
                "currency": "RUB"
            },
            "payment_method_data": {
                "type": "bank_card"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": url_for('payment_success', order_id=order_id, _external=True)
            },
            "metadata": {
                "order_id": order.id,
                "order_number": order.order_number
            },
            "description": f"Заказ {order.order_number} - 2SOUL Shop"
        }, uuid.uuid4())
        
        order.payment_id = payment.id
        order.payment_status = 'pending'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'confirmation_url': payment.confirmation.confirmation_url,
            'payment_id': payment.id
        })
    
    except Exception as e:
        print(f"Payment error: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@app.route('/payment/success/<int:order_id>')
def payment_success(order_id):
    """Payment success page."""
    order = Order.query.get_or_404(order_id)
    order.payment_status = 'succeeded'
    order.status = Order.STATUS_PROCESSING
    db.session.commit()
    
    return render_template('payment_success.html', order=order)

# ==================== Admin Routes ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page."""
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    form = AdminLoginForm()
    
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        
        if admin and check_password_hash(admin.password, form.password.data):
            login_user(admin, remember=True)
            flash('✓ Вы вошли в систему', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin_dashboard'))
        else:
            flash('✗ Неверные учетные данные', 'danger')
    
    return render_template('admin/login.html', form=form)

@app.route('/admin/logout')
@login_required
def admin_logout():
    """Admin logout."""
    logout_user()
    flash('✓ Вы вышли из системы', 'success')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard."""
    orders = Order.query.order_by(Order.created_at.desc()).all()
    
    stats = {
        'new_orders': len([o for o in orders if o.status == Order.STATUS_NEW]),
        'processing_orders': len([o for o in orders if o.status == Order.STATUS_PROCESSING]),
        'completed_orders': len([o for o in orders if o.status == Order.STATUS_COMPLETED]),
        'total_revenue': sum(o.total_amount for o in orders if o.status == Order.STATUS_COMPLETED)
    }
    
    return render_template('admin/dashboard.html', orders=orders, stats=stats)

# ==================== Admin API Routes ====================

@app.route('/api/admin/orders/<int:order_id>', methods=['GET'])
@login_required
def api_admin_get_order(order_id):
    """Get order details for admin."""
    order = Order.query.get_or_404(order_id)
    return jsonify({'order': order.to_dict()})

@app.route('/api/admin/orders/<int:order_id>', methods=['PUT'])
@login_required
def api_admin_update_order(order_id):
    """Update order status."""
    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    
    if 'status' in data and data['status'] in [s[0] for s in Order.STATUSES]:
        order.status = data['status']
        db.session.commit()
    
    return jsonify({'success': True, 'order': order.to_dict()})

@app.route('/api/admin/products', methods=['GET'])
@login_required
def api_admin_get_products():
    """Get all products for admin."""
    products = Product.query.all()
    return jsonify({'products': [p.to_dict() for p in products]})

@app.route('/api/admin/products', methods=['POST'])
@login_required
def api_admin_create_product():
    """Create a new product."""
    data = request.get_json()
    
    try:
        if not data.get('name'):
            return jsonify({'success': False, 'message': 'Название товара обязательно'}), 400
        if not data.get('price'):
            return jsonify({'success': False, 'message': 'Цена товара обязательна'}), 400
        if not data.get('category'):
            return jsonify({'success': False, 'message': 'Категория обязательна'}), 400
        if data.get('stock') is None:
            return jsonify({'success': False, 'message': 'Количество товара обязательно'}), 400
        
        product = Product(
            name=data.get('name'),
            description=data.get('description', ''),
            price=float(data.get('price')),
            category=data.get('category'),
            image_url=data.get('image_url', 'https://via.placeholder.com/400x500?text=Product'),
            stock=int(data.get('stock', 0))
        )
        
        sizes_str = data.get('sizes', 'XS, S, M, L, XL, XXL')
        sizes_list = [s.strip() for s in sizes_str.split(',') if s.strip()]
        if sizes_list:
            product.set_sizes(sizes_list)
        else:
            product.set_sizes(['One Size'])
        
        db.session.add(product)
        db.session.commit()
        
        print(f"✓ New product created: {product.name}")
        
        return jsonify({
            'success': True,
            'message': 'Товар успешно добавлен',
            'product': product.to_dict()
        })
    
    except ValueError as e:
        return jsonify({'success': False, 'message': f'Ошибка значения: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        print(f"ERROR creating product: {str(e)}")
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'}), 500

@app.route('/api/admin/products/<int:product_id>', methods=['PUT'])
@login_required
def api_admin_update_product(product_id):
    """Update product."""
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    try:
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            product.price = float(data['price'])
        if 'category' in data:
            product.category = data['category']
        if 'image_url' in data:
            product.image_url = data['image_url']
        if 'stock' in data:
            product.stock = int(data['stock'])
        if 'sizes' in data:
            sizes_list = [s.strip() for s in data['sizes'].split(',') if s.strip()]
            if sizes_list:
                product.set_sizes(sizes_list)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Товар успешно обновлен',
            'product': product.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'}), 500

@app.route('/api/admin/products/<int:product_id>', methods=['DELETE'])
@login_required
def api_admin_delete_product(product_id):
    """Delete product."""
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    
    print(f"✓ Product deleted: {product.name}")
    
    return jsonify({'success': True})

# ==================== Debug Routes ====================

@app.route('/api/debug/db', methods=['GET'])
def api_debug_db():
    """Debug database state."""
    products = Product.query.all()
    orders = Order.query.all()
    admins = Admin.query.all()
    
    return jsonify({
        'products_count': len(products),
        'orders_count': len(orders),
        'admins_count': len(admins),
        'products': [p.to_dict() for p in products],
    })

# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    print(f"Server error: {error}")
    return render_template('500.html'), 500

# ==================== CLI Commands ====================

@app.cli.command()
def init_database():
    """Initialize database."""
    init_db()

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Starting 2SOUL Shop")
    print("="*50)
    
    with app.app_context():
        db.create_all()
        init_db()
        
        # Show summary
        product_count = Product.query.count()
        order_count = Order.query.count()
        
        print(f"\n📊 Database Summary:")
        print(f"   - Products: {product_count}")
        print(f"   - Orders: {order_count}")
        print(f"\n🌐 Access the app at: http://localhost:5000")
        print(f"🔐 Admin panel: http://localhost:5000/admin/login")
        print("\n" + "="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
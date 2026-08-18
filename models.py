from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class Product(db.Model):
    """Product model."""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False, index=True)
    image_url = db.Column(db.String(500))
    sizes = db.Column(db.String(500))  # JSON: ["XS", "S", "M", "L", "XL"]
    stock = db.Column(db.Integer, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_sizes(self):
        """Get sizes as list."""
        if self.sizes:
            return json.loads(self.sizes)
        return ["One Size"]
    
    def set_sizes(self, sizes_list):
        """Set sizes from list."""
        self.sizes = json.dumps(sizes_list)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'image_url': self.image_url,
            'sizes': self.get_sizes(),
            'stock': self.stock
        }


class Order(db.Model):
    """Order model."""
    __tablename__ = 'orders'
    
    STATUS_NEW = 'new'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    
    STATUSES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('completed', 'Выполнен'),
        ('cancelled', 'Отменён')
    ]
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, index=True)
    customer_name = db.Column(db.String(255), nullable=False)
    customer_email = db.Column(db.String(255), nullable=False)
    customer_phone = db.Column(db.String(20))
    customer_address = db.Column(db.Text)
    
    items = db.Column(db.Text, nullable=False)  # JSON: [{"product_id": 1, "quantity": 2, "size": "M"}]
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default=STATUS_NEW)
    
    payment_id = db.Column(db.String(255), unique=True)  # YooKassa payment ID
    payment_status = db.Column(db.String(20))  # pending, succeeded, cancelled
    
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_items(self):
        """Get items as list."""
        if self.items:
            return json.loads(self.items)
        return []
    
    def set_items(self, items_list):
        """Set items from list."""
        self.items = json.dumps(items_list)
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'items': self.get_items(),
            'total_amount': self.total_amount,
            'status': self.status,
            'payment_status': self.payment_status,
            'created_at': self.created_at.isoformat()
        }


class Admin(UserMixin, db.Model):
    """Admin user model."""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Admin {self.username}>'
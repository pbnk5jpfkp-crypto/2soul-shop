from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError
from models import Admin

class AdminLoginForm(FlaskForm):
    """Admin login form."""
    username = StringField(
        'Имя пользователя',
        validators=[
            DataRequired(message='Введите имя пользователя'),
            Length(min=3, max=80, message='Длина должна быть от 3 до 80 символов')
        ],
        render_kw={
            'placeholder': 'admin',
            'autocomplete': 'username'
        }
    )
    
    password = PasswordField(
        'Пароль',
        validators=[
            DataRequired(message='Введите пароль'),
            Length(min=6, message='Пароль должен быть не менее 6 символов')
        ],
        render_kw={
            'placeholder': '••••••••',
            'autocomplete': 'current-password'
        }
    )
    
    submit = SubmitField('Войти в админ-панель')


class ProductForm(FlaskForm):
    """Product form for admin."""
    name = StringField(
        'Название товара',
        validators=[
            DataRequired(message='Введите название'),
            Length(min=3, max=255, message='Название должно быть от 3 до 255 символов')
        ],
        render_kw={'placeholder': 'Например: Premium Hoodie'}
    )
    
    description = TextAreaField(
        'Описание',
        validators=[
            DataRequired(message='Введите описание'),
            Length(min=10, max=1000, message='Описание должно быть от 10 до 1000 символов')
        ],
        render_kw={'placeholder': 'Подробное описание товара...', 'rows': 4}
    )
    
    price = FloatField(
        'Цена (₽)',
        validators=[
            DataRequired(message='Введите цену'),
            NumberRange(min=0.01, message='Цена должна быть больше 0')
        ],
        render_kw={'placeholder': '2990'}
    )
    
    category = StringField(
        'Категория',
        validators=[
            DataRequired(message='Введите категорию'),
            Length(min=2, max=100, message='Категория должна быть от 2 до 100 символов')
        ],
        render_kw={'placeholder': 'Например: Одежда, Обувь, Аксессуары'}
    )
    
    image_url = StringField(
        'URL изображения',
        validators=[Length(max=500)],
        render_kw={'placeholder': 'https://example.com/image.jpg'}
    )
    
    stock = IntegerField(
        'Количество в наличии',
        validators=[
            DataRequired(message='Введите количество'),
            NumberRange(min=0, message='Количество не может быть отрицательным')
        ],
        render_kw={'placeholder': '50'}
    )
    
    sizes = StringField(
        'Размеры (через запятую)',
        render_kw={'placeholder': 'XS, S, M, L, XL, XXL'}
    )
    
    submit = SubmitField('Добавить товар')
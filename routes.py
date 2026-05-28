from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Product, Cart, Order, OrderItem
from forms import LoginForm, RegisterForm, ProductForm
from datetime import datetime, timedelta

routes = Blueprint('routes', __name__)

# проверка прав админа
def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Доступ запрещён')
            return redirect(url_for('routes.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# главная страница - список товаров
@routes.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

# страница товара
@routes.route('/product/<int:id>')
def product(id):
    product = db.session.get(Product, id)
    if not product:
        flash('Товар не найден')
        return redirect(url_for('routes.index'))
    return render_template('index.html', product=product, detail=True)

# вход
@routes.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Добро пожаловать')
            return redirect(url_for('routes.index'))
        flash('Неверный логин или пароль')
    return render_template('login.html', form=form)

# регистрация
@routes.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Имя занято')
        else:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Регистрация успешна')
            return redirect(url_for('routes.index'))
    return render_template('login.html', form=form, register=True)

# выход
@routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.index'))

# профиль пользователя
@routes.route('/profile')
@login_required
def profile():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).all()
    return render_template('profile.html', user=current_user, orders=orders)

# корзина
@routes.route('/cart')
@login_required
def cart():
    total = sum(i.quantity * i.product.price for i in current_user.cart_items)
    return render_template('cart.html', cart_items=current_user.cart_items, total=total)

# добавление в корзину
@routes.route('/add/<int:pid>', methods=['POST'])
@login_required
def add(pid):
    product = db.session.get(Product, pid)
    if not product:
        flash('Товар не найден')
        return redirect(url_for('routes.index'))
    
    # получаем количество из формы
    quantity = int(request.form.get('quantity', 1))
    if quantity < 1:
        quantity = 1
    if quantity > 99:
        quantity = 99
    
    # если уже есть в корзине - увеличиваем количество
    item = Cart.query.filter_by(user_id=current_user.id, product_id=pid).first()
    if item:
        item.quantity += quantity
    else:
        item = Cart(user_id=current_user.id, product_id=pid, quantity=quantity)
        db.session.add(item)
    db.session.commit()
    flash(f'Добавлено в корзину: {quantity} шт')
    return redirect(request.referrer or url_for('routes.index'))

# удаление из корзины
@routes.route('/remove/<int:cid>')
@login_required
def remove(cid):
    item = db.session.get(Cart, cid)
    if item and item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
        flash('Удалено')
    return redirect(url_for('routes.cart'))

# оформление заказа
@routes.route('/checkout', methods=['POST'])
@login_required
def checkout():
    if not current_user.cart_items:
        flash('Корзина пуста')
        return redirect(url_for('routes.cart'))
    
    # считаем сумму
    total = sum(i.quantity * i.product.price for i in current_user.cart_items)
    
    # создаём заказ с датой доставки +10 дней
    order = Order(
        user_id=current_user.id,
        total_price=total,
        delivery_date=datetime.utcnow() + timedelta(days=10)
    )
    db.session.add(order)
    db.session.flush()  # получаем id заказа
    
    # переносим товары из корзины в заказ
    for item in current_user.cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_name=item.product.name,
            product_price=item.product.price,
            quantity=item.quantity
        )
        db.session.add(order_item)
        db.session.delete(item)
    
    db.session.commit()
    flash('Заказ оформлен! Доставка через 10 дней')
    return redirect(url_for('routes.profile'))

# админ панель - список товаров
@routes.route('/admin')
@login_required
@admin_required
def admin():
    products = Product.query.all()
    return render_template('admin.html', products=products)

# добавление товара (админ)
@routes.route('/admin/product/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            price=form.price.data,
            category=form.category.data,
            image_url=form.image_url.data
        )
        db.session.add(product)
        db.session.commit()
        flash('Товар добавлен')
        return redirect(url_for('routes.admin'))
    return render_template('edit_product.html', form=form, title='Добавить товар')

# редактирование товара (админ)
@routes.route('/admin/product/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(id):
    product = db.session.get(Product, id)
    if not product:
        flash('Товар не найден')
        return redirect(url_for('routes.admin'))
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.name = form.name.data
        product.price = form.price.data
        product.category = form.category.data
        product.image_url = form.image_url.data
        db.session.commit()
        flash('Товар обновлён')
        return redirect(url_for('routes.admin'))
    return render_template('edit_product.html', form=form, title='Редактировать товар')

# удаление товара (админ)
@routes.route('/admin/product/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_product(id):
    product = db.session.get(Product, id)
    if product:
        Cart.query.filter_by(product_id=id).delete()  # удаляем из корзин
        db.session.delete(product)
        db.session.commit()
        flash('Товар удалён')
    return redirect(url_for('routes.admin'))
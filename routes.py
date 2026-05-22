from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Product, Cart

routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    return render_template('index.html', products=Product.query.all())

@routes.route('/product/<int:id>')
def product(id):
    return render_template('index.html', product=db.session.get(Product, id), detail=True)

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password_hash, request.form['password']):
            login_user(user)
            flash('Добро пожаловать!')
            return redirect(url_for('routes.index'))
        flash('Неверный логин')
    return render_template('login.html')

@routes.route('/register', methods=['POST'])
def register():
    if User.query.filter_by(username=request.form['username']).first():
        flash('Имя занято')
    else:
        user = User(username=request.form['username'], 
                   password_hash=generate_password_hash(request.form['password']))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Регистрация успешна!')
        return redirect(url_for('routes.index'))
    return render_template('login.html')

@routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.index'))

@routes.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@routes.route('/cart')
@login_required
def cart():
    total = sum(i.quantity * i.product.price for i in current_user.cart_items)
    return render_template('cart.html', cart_items=current_user.cart_items, total=total)

@routes.route('/add/<int:pid>', methods=['POST'])
@login_required
def add(pid):
    item = Cart.query.filter_by(user_id=current_user.id, product_id=pid).first()
    if item:
        item.quantity += 1
    else:
        item = Cart(user_id=current_user.id, product_id=pid, quantity=1)
        db.session.add(item)
    db.session.commit()
    flash('Добавлено в корзину!')
    return redirect(request.referrer or url_for('routes.index'))

@routes.route('/remove/<int:cid>')
@login_required
def remove(cid):
    item = db.session.get(Cart, cid)
    if item and item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
        flash('Удалено')
    return redirect(url_for('routes.cart'))

@routes.route('/checkout', methods=['POST'])
@login_required
def checkout():
    for item in current_user.cart_items:
        db.session.delete(item)
    db.session.commit()
    flash('Заказ оформлен! Hala Madrid!')
    return redirect(url_for('routes.profile'))
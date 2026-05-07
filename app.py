from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = '12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ============ МОДЕЛИ ============
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    user = db.relationship('User', backref='cart_items')
    product = db.relationship('Product')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ============ МАРШРУТЫ ============
@app.route('/')
def index():
    return render_template('index.html', products=Product.query.all())

@app.route('/product/<int:id>')
def product(id):
    return render_template('index.html', product=Product.query.get_or_404(id), detail=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password_hash, request.form['password']):
            login_user(user)
            flash('Добро пожаловать!')
            return redirect(url_for('index'))
        flash('Неверный логин')
    return render_template('login.html')

@app.route('/register', methods=['POST'])
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
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/cart')
@login_required
def cart():
    total = sum(i.quantity * i.product.price for i in current_user.cart_items)
    return render_template('cart.html', cart_items=current_user.cart_items, total=total)

@app.route('/add/<int:pid>', methods=['POST'])
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
    return redirect(request.referrer or url_for('index'))

@app.route('/remove/<int:cid>')
@login_required
def remove(cid):
    item = Cart.query.get_or_404(cid)
    if item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
        flash('Удалено')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    for item in current_user.cart_items:
        db.session.delete(item)
    db.session.commit()
    flash('Заказ оформлен! Hala Madrid!')
    return redirect(url_for('profile'))

# ============ API ============
@app.route('/api/products', methods=['GET', 'POST'])
def api_products():
    if request.method == 'GET':
        return jsonify([{'id': p.id, 'name': p.name, 'price': p.price} for p in Product.query.all()])
    data = request.json
    p = Product(name=data['name'], price=data['price'], category=data.get('category', 'Общее'))
    db.session.add(p)
    db.session.commit()
    return jsonify({'id': p.id}), 201

@app.route('/api/products/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def api_product(id):
    p = Product.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify({'id': p.id, 'name': p.name, 'price': p.price})
    if request.method == 'PUT':
        data = request.json
        p.name = data.get('name', p.name)
        p.price = data.get('price', p.price)
        db.session.commit()
        return jsonify({'message': 'updated'})
    db.session.delete(p)
    db.session.commit()
    return jsonify({'message': 'deleted'})

# ============ ИНИЦИАЛИЗАЦИЯ ============
with app.app_context():
    db.create_all()
    if Product.query.count() == 0:
        products = [
            Product(name='Домашняя форма 24/25', price=89.99, category='Формы'),
            Product(name='Гостевая форма 24/25', price=89.99, category='Формы'),
            Product(name='Шарф фаната', price=19.99, category='Аксессуары'),
            Product(name='Бейсболка RM', price=24.99, category='Аксессуары'),
        ]
        for p in products:
            db.session.add(p)
        if not User.query.filter_by(username='fan').first():
            db.session.add(User(username='fan', password_hash=generate_password_hash('123')))
        db.session.commit()
        print('✅ Готово! fan / 123')

if __name__ == '__main__':
    app.run(debug=True)
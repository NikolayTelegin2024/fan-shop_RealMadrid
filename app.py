from flask import Flask
from config import Config
from models import db
from flask_login import LoginManager
from routes import routes
from api import api

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    login_manager = LoginManager(app)
    login_manager.login_view = 'login'
    
    from models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    app.register_blueprint(routes)
    app.register_blueprint(api, url_prefix='/api')
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        
        from models import Product, User
        from werkzeug.security import generate_password_hash
        
        if Product.query.count() == 0:
            products = [
                Product(name='Домашняя форма 25/26', price=89.99, category='Формы', image_url='https://dealersport.ru/wp-content/smush-webp/2025/07/форма-реал-мадрид-2025-2026.jpg.webp'),
                Product(name='Гостевая форма 25/26', price=89.99, category='Формы', image_url='https://olimpijka.ru/files/products/07/rmawakids.600x800.png?3b20897b642c65b9da192c394d2cb747'),
                Product(name='Шарф фаната', price=19.99, category='Аксессуары', image_url='https://dealersport.ru/wp-content/smush-webp/2020/03/81oHalwk7uL-scaled.jpeg.webp'),
                Product(name='Бейсболка RM', price=24.99, category='Аксессуары', image_url='https://olimpijka.ru/files/products/ao-mpl.600x800.jpg?2e26c97ed8f505ba91f1c663410f0709'),
            ]
            for p in products:
                db.session.add(p)
            if not User.query.filter_by(username='fan').first():
                db.session.add(User(username='fan', password_hash=generate_password_hash('123')))
            db.session.commit()
            print('Готово! fan / 123')
    
    app.run(debug=True)
from flask import Flask, render_template
from config import Config
from models import db
from flask_login import LoginManager
from routes import routes
from api import api

# создание приложения
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # подключаем базу данных
    db.init_app(app)
    
    # настройка авторизации
    login_manager = LoginManager(app)
    login_manager.login_view = 'routes.login'
    login_manager.login_message = 'Пожалуйста, войдите'
    
    from models import User
    
    # загрузка пользователя по id из сессии
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    # обработка ошибки 404 - страница не найдена
    @app.errorhandler(404)
    def not_found(error):
        return render_template('base.html', content='<h1>404 - Страница не найдена</h1><p>Такой страницы нет</p><a href="/" class="btn">На главную</a>'), 404
    
    # обработка ошибки 403 - доступ запрещён
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('base.html', content='<h1>403 - Доступ запрещён</h1><p>Нет прав</p><a href="/" class="btn">На главную</a>'), 403
    
    # обработка ошибки 500 - ошибка сервера
    @app.errorhandler(500)
    def server_error(error):
        return render_template('base.html', content='<h1>500 - Ошибка сервера</h1><p>Что-то сломалось</p><a href="/" class="btn">На главную</a>'), 500
    
    # регистрируем маршруты сайта и api
    app.register_blueprint(routes)
    app.register_blueprint(api, url_prefix='/api')
    
    return app

# запуск
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # создаём таблицы в базе если их нет
        db.create_all()
        
        from models import Product, User
        
        # создаём админа если нет
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@shop.com', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('админ создан: admin / admin123')
        
        # создаём товары для примера если база пустая
        if Product.query.count() == 0:
            products = [
                Product(name='Домашняя форма 25/26', price=8990, category='Формы', image_url='https://dealersport.ru/wp-content/smush-webp/2025/07/форма-реал-мадрид-2025-2026.jpg.webp'),
                Product(name='Гостевая форма 25/26', price=8990, category='Формы', image_url='https://olimpijka.ru/files/products/07/rmawakids.600x800.png?3b20897b642c65b9da192c394d2cb747'),
                Product(name='Шарф фаната', price=1990, category='Аксессуары', image_url='https://dealersport.ru/wp-content/smush-webp/2020/03/81oHalwk7uL-scaled.jpeg.webp'),
                Product(name='Бейсболка RM', price=2490, category='Аксессуары', image_url='https://olimpijka.ru/files/products/ao-mpl.600x800.jpg?2e26c97ed8f505ba91f1c663410f0709'),
            ]
            for p in products:
                db.session.add(p)
            
            # создаём обычного пользователя для тестов
            if not User.query.filter_by(username='fan').first():
                fan = User(username='fan', email='fan@realmadrid.com')
                fan.set_password('123')
                db.session.add(fan)
            db.session.commit()
            print('готово! fan / 123, admin / admin123')
    
    app.run(debug=True)
# настройки приложения
class Config:
    SECRET_KEY = '12345'  # ключ для сессий
    SQLALCHEMY_DATABASE_URI = 'sqlite:///shop.db'  # путь к базе данных
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # отключаем лишние уведомления
    WTF_CSRF_ENABLED = True  # защита форм
    WTF_CSRF_SECRET_KEY = 'csrf_secret_key_12345'  # ключ для защиты форм
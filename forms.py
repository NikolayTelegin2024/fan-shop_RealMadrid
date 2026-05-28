from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, PasswordField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

# форма для товаров (админка)
class ProductForm(FlaskForm):
    id = HiddenField()
    name = StringField('Название', validators=[DataRequired(), Length(min=2, max=100)])
    price = FloatField('Цена', validators=[DataRequired(), NumberRange(min=0, max=10000)])
    category = SelectField('Категория', choices=[('Формы', 'Формы'), ('Аксессуары', 'Аксессуары')])
    image_url = StringField('Ссылка на фото', validators=[Optional(), Length(max=300)])

# форма входа
class LoginForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired(), Length(min=2, max=80)])
    password = PasswordField('Пароль', validators=[DataRequired()])

# форма регистрации
class RegisterForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired(), Length(min=2, max=80)])
    email = StringField('Email', validators=[Optional(), Length(max=120)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=3, max=100)])
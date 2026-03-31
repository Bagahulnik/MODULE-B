# D:\MODULE B\app\forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    login = StringField(
        "Логин (email/телефон)",
        validators=[DataRequired(message="Введите email или телефон")],
        render_kw={"placeholder": "example@email.com или 77771234567"}
    )
    password = PasswordField(
        "Пароль",
        validators=[DataRequired(message="Введите пароль")],
        render_kw={"type": "password"}
    )
    submit = SubmitField("Войти")

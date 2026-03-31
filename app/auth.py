# D:\MODULE B\app\auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager
from app.models import User

bp = Blueprint("auth", __name__)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("routes.home"))

    if request.method == "POST":
        login_input = request.form.get("login").strip()
        password = request.form.get("password")

        user = User.query.filter(
            (User.email == login_input) | (User.phone == login_input)
        ).first()

        if user:
            print("Нашли пользователя в login:", user.id, user.email, user.role)
            print("Password_hash хранится как:", repr(user.password_hash))
            is_ok = check_password_hash(user.password_hash, password)
            print("check_password_hash:", is_ok)
            if user.role == "moderator" and is_ok:
                login_user(user)
                print("Пользователь теперь:", current_user.id)
                print("is_authenticated:", current_user.is_authenticated)
                flash("Вы авторизованы как модератор.", "success")
                return redirect(url_for("routes.home"))
        flash("Неверный логин/пароль или нет роли модератора.", "error")


    return render_template("auth/login.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из админ‑панели.", "info")
    return redirect(url_for("auth.login"))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

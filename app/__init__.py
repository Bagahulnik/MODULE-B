# D:\MODULE B\app\__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config["SECRET_KEY"] = "very-secret-key-for-college"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # ===== Импорт и регистрация Blueprint'ов =====
    from app import routes, auth, models

    app.register_blueprint(auth.bp)   
    app.register_blueprint(routes.bp)   # <-- это самое важное
   

    # =================================================
    # Создание таблиц при старте
    with app.app_context():
        db.create_all()

    return app

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db
from datetime import datetime, timedelta


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="user")

    adverts = db.relationship("Advert", back_populates="user", lazy=True)


class PaidService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)


class AdvertPaidService(db.Model):
    __tablename__ = "advert_paid_service"

    id = db.Column(db.Integer, primary_key=True)

    advert_id = db.Column(
        db.Integer, db.ForeignKey("advert.id"), nullable=False
    )
    advert = db.relationship("Advert", back_populates="paid_services_rel")

    service_id = db.Column(
        db.Integer, db.ForeignKey("paid_service.id"), nullable=False
    )
    service = db.relationship("PaidService")

    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)

    def __init__(self, advert, service, duration_days):
        self.advert = advert
        self.service = service
        self.start_date = datetime.utcnow()
        self.end_date = self.start_date + timedelta(days=duration_days)

    @property
    def is_active(self):
        return self.end_date and self.end_date > datetime.utcnow()

    @property
    def is_expired(self):
        return self.end_date and self.end_date <= datetime.utcnow()


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    adverts = db.relationship(
        "Advert", back_populates="category", cascade="all, delete-orphan"
    )


class Advert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    text = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    views = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default="moderation")
    created_at = db.Column(db.DateTime, default=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", back_populates="adverts")

    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    category = db.relationship("Category", back_populates="adverts")

    # связь с адъюнкт‑таблицей
    paid_services_rel = db.relationship(
        "AdvertPaidService",
        back_populates="advert",
        lazy=True
    )

    # это свойство возвращает AdvertPaidService, а не PaidService
    @property
    def paid_services(self):
        return self.paid_services_rel

# D:\MODULE B\app\routes.py
from app.utils import export_adverts_csv
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_


from app import db
from app.models import User, Advert, Category

bp = Blueprint("routes", __name__)

@bp.route("/")
@login_required
def home():
    total_users = User.query.count()
    total_adverts = Advert.query.count()
    published_adverts = Advert.query.filter_by(status="published").count()
    moderation_adverts = Advert.query.filter_by(status="moderation").count()
    declined_adverts = Advert.query.filter_by(status="declined").count()

    top_adverts = (
        Advert.query
        .filter_by(status="published")
        .order_by(Advert.views.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "admin/home.html",
        total_users=total_users,
        total_adverts=total_adverts,
        published_adverts=published_adverts,
        moderation_adverts=moderation_adverts,
        declined_adverts=declined_adverts,
        top_adverts=top_adverts,
    )

@bp.route("/categories")
@login_required
def categories():
    all_cats = Category.query.all()
    cat_stats = []
    for cat in all_cats:
        pub_count = Advert.query.filter(
            Advert.category_id == cat.id,
            Advert.status == "published"
        ).count()
        cat_stats.append((cat, pub_count))
    return render_template("admin/categories.html", cat_stats=cat_stats)

@bp.route("/users")
@login_required
def users():
    search = request.args.get("search", "").strip()
    query = User.query

    if search:
        # число → ищем по ID
        try:
            search_int = int(search)
            query = query.filter(User.id == search_int)
            print("SEARCH by ID:", search_int)
        except ValueError:
            # ищем по name, phone, email (как часть строки)
            query = query.filter(
                or_(
                    User.name.contains(search),
                    User.phone.contains(search),
                    User.email.contains(search),
                )
            )
            print("SEARCH by text:", repr(search))

    users = query.all()
    user_stats = []
    for user in users:
        pub_count = Advert.query.filter(
            Advert.user_id == user.id,
            Advert.status == "published"
        ).count()
        user_stats.append((user, pub_count))

    return render_template("admin/users.html", user_stats=user_stats, search=search)


@bp.route("/adverts")
@login_required
def adverts():
    status = request.args.get("status", "")
    category_id = request.args.get("category_id", type=int)
    text = request.args.get("text", "").strip()

    query = Advert.query

    if status:
        query = query.filter_by(status=status)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if text:
        query = query.join(Category, Category.id == Advert.category_id) \
                     .join(User, User.id == Advert.user_id)
        query = query.filter(
            or_(
                Advert.title.contains(text),
                Advert.text.contains(text),
                Category.name.contains(text),
                User.name.contains(text)
            )
        )

    adverts = query.all()
    categories = Category.query.all()

    return render_template("admin/adverts.html", adverts=adverts, categories=categories)

@bp.route("/advert/<int:advert_id>")
@login_required
def advert_detail(advert_id):
    advert = Advert.query.get_or_404(advert_id)
    return render_template("admin/advert_detail.html", advert=advert)

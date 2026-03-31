from app.utils import export_adverts_csv
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, current_user
from sqlalchemy import or_
from datetime import datetime


from app import db
from app.models import User, Advert, Category, PaidService, AdvertPaidService


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
        try:
            search_int = int(search)
            query = query.filter(User.id == search_int)
        except ValueError:
            query = query.filter(
                or_(
                    User.name.contains(search),
                    User.phone.contains(search),
                    User.email.contains(search),
                )
            )

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

    # Подключённые сервисы (AdvertPaidService)
    # available_services — все PaidService, у которых нет активной связи с этим advert
    active_service_ids = [
        ps.service_id
        for ps in advert.paid_services_rel
        if ps.is_active
    ]
    available_services = PaidService.query.filter(
        PaidService.id.not_in(active_service_ids)
    ).all()

    return render_template(
        "admin/advert_detail.html",
        advert=advert,
        available_services=available_services
    )


@bp.route("/advert/<int:advert_id>/status", methods=["POST"])
@login_required
def advert_status(advert_id):
    advert = Advert.query.get_or_404(advert_id)
    status = request.form.get("status")
    valid_transitions = {
        "moderation": ["published", "declined"],
        "published": ["declined"],
    }

    if status not in valid_transitions.get(advert.status, []):
        flash("Нельзя перевести в этот статус.", "error")
        return redirect(url_for("routes.advert_detail", advert_id=advert_id))

    advert.status = status
    db.session.commit()

    flash(f"Статус изменён на «{advert.status}».")
    return redirect(url_for("routes.advert_detail", advert_id=advert_id))


@bp.route("/advert/<int:advert_id>/link_service/<int:service_id>", methods=["POST"])
@login_required
def link_service(advert_id, service_id):
    advert = Advert.query.get_or_404(advert_id)
    service = PaidService.query.get_or_404(service_id)

    existing = AdvertPaidService.query.filter_by(
        advert_id=advert_id,
        service_id=service_id
    ).first()

    if existing:
        if existing.is_active:
            flash("Услуга уже подключена и активна.", "info")
            return redirect(url_for("routes.advert_detail", advert_id=advert_id))
        db.session.delete(existing)

    new_link = AdvertPaidService(
        advert=advert,
        service=service,
        duration_days=service.duration_days
    )
    db.session.add(new_link)
    db.session.commit()

    flash(f"Услуга «{service.name}» подключена к объявлению.")
    return redirect(url_for("routes.advert_detail", advert_id=advert_id))


@bp.route("/advert/<int:advert_id>/unlink_service/<int:service_id>", methods=["POST"])
@login_required
def unlink_service(advert_id, service_id):
    advert = Advert.query.get_or_404(advert_id)
    link = AdvertPaidService.query.filter_by(
        advert_id=advert_id,
        service_id=service_id
    ).first()

    if not link:
        flash("Связь услуги не найдена.", "error")
        return redirect(url_for("routes.advert_detail", advert_id=advert_id))

    db.session.delete(link)
    db.session.commit()

    flash("Услуга отключена от объявления.")
    return redirect(url_for("routes.advert_detail", advert_id=advert_id))


# ========== API категорий ==========

@bp.route("/api/categories", methods=["GET", "POST"])
@login_required
def api_categories():
    if request.method == "GET":
        categories = Category.query.all()
        cat_stats = []
        for cat in categories:
            pub_count = Advert.query.filter(
                Advert.category_id == cat.id,
                Advert.status == "published"
            ).count()
            cat_stats.append({
                "id": cat.id,
                "name": cat.name,
                "pub_count": pub_count,
            })
        return jsonify(cat_stats)

    if request.method == "POST":
        data = request.get_json()
        name = data.get("name", "").strip()

        if not name:
            return jsonify({"error": "Название не может быть пустым"}), 400

        existing = Category.query.filter_by(name=name).first()
        if existing:
            return jsonify({"error": "Категория с таким названием уже существует"}), 409

        new_cat = Category(name=name)
        db.session.add(new_cat)
        db.session.commit()

        pub_count = 0

        return jsonify({
            "id": new_cat.id,
            "name": new_cat.name,
            "pub_count": pub_count,
        }), 201


@bp.route("/api/categories/<int:cat_id>", methods=["PUT", "DELETE"])
@login_required
def api_category(cat_id):
    cat = Category.query.get_or_404(cat_id)

    if request.method == "PUT":
        data = request.get_json()
        name = data.get("name", "").strip()

        if not name:
            return jsonify({"error": "Название не может быть пустым"}), 400

        existing = Category.query.filter(
            Category.id != cat_id,
            Category.name == name
        ).first()
        if existing:
            return jsonify({"error": "Категория с таким названием уже существует"}), 409

        cat.name = name
        db.session.commit()

        pub_count = Advert.query.filter(
            Advert.category_id == cat.id,
            Advert.status == "published"
        ).count()

        return jsonify({
            "id": cat.id,
            "name": cat.name,
            "pub_count": pub_count,
        })

    if request.method == "DELETE":
        has_adverts = db.session.query(Advert.id).filter(Advert.category_id == cat_id).first()
        if has_adverts:
            return jsonify({"error": "Категорию, к которой привязаны объявления, удалить нельзя"}), 400

        db.session.delete(cat)
        db.session.commit()

        return jsonify({"id": cat_id, "success": "Категория удалена"}), 200

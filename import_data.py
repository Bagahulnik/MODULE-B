# D:\MODULE B\import_data.py
from app import create_app, db
from app.models import User, Category, Advert
from werkzeug.security import generate_password_hash


app = create_app()

with app.app_context():
    db.drop_all()   
    db.create_all()

    # 1. Load users.csv -> email → user.id
    email_to_user_id = {}
    with open("media-files/data/users.csv", encoding="utf-8") as f:
        import csv
        reader = csv.DictReader(f)
        for row in reader:
            # Важно: row["password"] у тебя <hash(...)> — просто возьмём как строку
            user = User(
                name=row["name"],
                phone=row["phone"],
                email=row["email"],
                password_hash=generate_password_hash("123"),  # или dummy_hash, если хэши фейковые
                role=row["role"],
            )
            db.session.add(user)
            db.session.flush()
            email_to_user_id[row["email"]] = user.id

    # 2. Load categories.csv -> id → category.id
    code_to_cat_id = {}
    with open("media-files/data/categories.csv", encoding="utf-8") as f:
        import csv
        reader = csv.DictReader(f)
        for row in reader:
            code = row["id"]        # C1, C2, ...
            name = row["name"]
            cat = Category(name=name)
            db.session.add(cat)
            db.session.flush()
            code_to_cat_id[code] = cat.id

    # 3. Load adverts.csv -> связать author↔email, category↔id
    with open("media-files/data/adverts.csv", encoding="utf-8") as f:
        import csv
        reader = csv.DictReader(f)
        for row in reader:
            # 3.1. Найти user_id по email в поле `author`
            # формат: [ethan@example.com]
            author = row["author"].strip("[]")  # убираем [ ... ]
            if author not in email_to_user_id:
                print(f"WARNING: автор с email '{author}' не найден")
                continue
            user_id = email_to_user_id[author]

            # 3.2. Найти category_id по `category` (C1, C2, ...)
            cat_code = row["category"].strip()
            if cat_code not in code_to_cat_id:
                print(f"WARNING: категория '{cat_code}' не найдена")
                continue
            category_id = code_to_cat_id[cat_code]

            # 3.3. Создать объявление
            advert = Advert(
                title=row["title"],
                text=row["text"],
                price=float(row["price"]),
                views=int(row["views_count"]),
                status=row["status"],
                user_id=user_id,
                category_id=category_id,
            )
            db.session.add(advert)

    db.session.commit()
    print("Данные импортированы успешно.")

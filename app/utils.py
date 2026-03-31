# D:\MODULE B\app\utils.py
import csv
import io
from flask import Response

def export_adverts_csv(adverts):
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Заголовок",
        "Категория",
        "Цена",
        "Телефон автора",
        "Email автора",
        "Текст",
        "Дата размещения"
    ])

    for advert in adverts:
        writer.writerow([
            advert.id,
            advert.title,
            advert.category.name,
            str(advert.price),
            advert.user.phone,
            advert.user.email,
            advert.text,
            advert.created_at.strftime("%Y-%m-%d %H:%M:%S")
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=export_adverts.csv"}
    )

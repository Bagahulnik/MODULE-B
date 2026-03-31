# D:\MODULE B\run.py
from app import create_app, db
from app.models import User, Advert, Category

app = create_app()

@app.before_request
def create_tables():
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

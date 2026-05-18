from app import create_app
from app.database import db
from seed_data.seed import seed_db

app = create_app("development")

with app.app_context():
    db.create_all()
    seed_db()

if __name__ == "__main__":
    app.run(debug=True, port=5000)

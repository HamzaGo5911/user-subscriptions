from app import create_app
from app import db

app_data = create_app()
from flask_migrate import Migrate

app, mail, scheduler = app_data[:3]

migrate = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int("5000"), debug=True)

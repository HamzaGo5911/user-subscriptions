from flask import Flask
from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler
from config.config import Config
from app.routes import create_subscription_job, main
from app.models import db

scheduler = BackgroundScheduler()


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    mail = Mail()

    db.init_app(app)

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'hamza.golang@gmail.com'
    app.config['MAIL_PASSWORD'] = 'dkws fdss flmn jkbp'
    app.config['MAIL_DEFAULT_SENDER'] = 'hamza.golang@gmail.com'

    mail.init_app(app)

    scheduler.start()
    scheduler.add_job(create_subscription_job, 'interval', minutes=2, id='subscription_job', args=(app,))

    app.register_blueprint(main)

    return app, db, mail, scheduler

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    age = db.Column(db.Integer)

    def __repr__(self):
        return f'<User {self.username}>'


class Feature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return f'<Feature {self.name}>'


class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    feature_id = db.Column(db.Integer, db.ForeignKey('feature.id'), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_feature_enabled = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref=db.backref('subscriptions', lazy=True))
    feature = db.relationship('Feature', backref=db.backref('subscriptions', lazy=True))

    def __repr__(self):
        return f'<Subscription {self.id} for User {self.user.username} - Feature {self.feature.name}>'


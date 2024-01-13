import os

from flask_mail import Mail, Message

from celery import Celery
from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from app import db, app
from app.models import User, Feature, Subscription


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'name': user.name
        }
        return jsonify(user_data), 200
    except SQLAlchemyError as e:
        return jsonify({"message": str(e)}), 500


@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()

    existing_user = User.query.filter(
        (User.email == data['email']) | (User.username == data['username'])
    ).first()

    if existing_user:
        return jsonify({'error': 'User with this email or username already exists'}), 400

    new_user = User(email=data['email'], username=data['username'], name=data.get('name', ''), age=data.get('age' ''))

    db.session.add(new_user)
    db.session.commit()

    response = {
        'user': {
            'id': new_user.id,
            'email': new_user.email,
            'name': new_user.name,
            'username': new_user.username,
            'age': new_user.age,
        }
    }

    return jsonify(response), 201


@app.route('/users/<int:user_id>', methods=['PATCH'])
def update_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        for key, value in data.items():
            setattr(user, key, value)
        db.session.commit()
        return jsonify({"message": "User updated successfully"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@app.route('/users', methods=['GET'])
def get_all_users():
    try:
        users = User.query.all()

        user_list = []
        for user in users:
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'name': user.name
            }
            user_list.append(user_data)

        return jsonify({'users': user_list}), 200
    except SQLAlchemyError as e:
        return jsonify({"message": str(e)}), 500


@app.route('/features', methods=['POST'])
def create_feature():
    data = request.get_json()

    if 'name' not in data or 'description' not in data:
        return jsonify({'error': 'Name and description are required'}), 400

    existing_feature = Feature.query.filter_by(name=data['name']).first()

    if existing_feature:
        return jsonify({'error': 'Feature with this name already exists'}), 400

    new_feature = Feature(name=data['name'], description=data['description'])

    try:
        db.session.add(new_feature)
        db.session.commit()

        response = {
            'feature': {
                'id': new_feature.id,
                'name': new_feature.name,
                'description': new_feature.description
            }
        }

        return jsonify(response), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@app.route('/features', methods=['GET'])
def get_all_features():
    try:
        features = Feature.query.all()

        feature_list = []
        for feature in features:
            feature_data = {
                'id': feature.id,
                'name': feature.name,
                'description': feature.description
            }
            feature_list.append(feature_data)

        return jsonify({'features': feature_list}), 200
    except SQLAlchemyError as e:
        return jsonify({"message": str(e)}), 500


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'hamza.golang@gmail.com'
app.config['MAIL_PASSWORD'] = os.environ.get('USERNAME_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = 'hamza.golang@gmail.com'

mail = Mail(app)

app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


@celery.task
def send_async_email(subject, body, recipient):
    msg = Message(subject=subject, sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[recipient])
    msg.body = body
    mail.send(msg)


@app.route('/subscribe', methods=['POST'])
def create_subscription():
    data = request.get_json()

    user_id = data.get('user_id')
    feature_id = data.get('feature_id')
    is_feature_enabled = data.get('feature', False)

    user = User.query.get(user_id)
    feature = Feature.query.get(feature_id)

    if not user or not feature:
        return jsonify({'error': 'User or Feature not found'}), 404

    existing_subscription = (Subscription.query.filter_by(user_id=user_id, feature_id=feature_id,
                                                          is_feature_enabled=is_feature_enabled).first())

    if existing_subscription:
        return jsonify({'error': 'User is already subscribed to this feature'}), 400

    new_subscription = Subscription(user_id=user_id, feature_id=feature_id, is_feature_enabled=is_feature_enabled)

    db.session.add(new_subscription)
    db.session.commit()

    email_subject = 'Wan clouds'
    recipient_email = user.email
    msg = Message(subject='Wan clouds Email', sender=app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[recipient_email])

    if is_feature_enabled:
        msg.body = f"Hello! You have subscribed to the feature: {feature.name}"
    else:
        msg.body = "Hello! You don't have any features subscribed."

    send_async_email(email_subject, msg.body, recipient_email)

    response = {
        'subscription': {
            'id': new_subscription.id,
            'user_id': new_subscription.user_id,
            'feature_id': new_subscription.feature_id,
            'start_date': new_subscription.start_date,
            'is_active': new_subscription.is_active,
            'is_feature_enabled': new_subscription.is_feature_enabled
        }
    }

    return jsonify(response), 201

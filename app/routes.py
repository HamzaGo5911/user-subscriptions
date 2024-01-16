from flask import Blueprint, jsonify, request
from flask import render_template
from flask_mail import Message, Mail
from sqlalchemy.exc import SQLAlchemyError
from .models import User, Feature, Subscription, db

main = Blueprint('main', __name__)
mail = Mail()


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/users/<int:user_id>', methods=['GET'])
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


@main.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()

    existing_user = User.query.filter(
        (User.email == data['email']) | (User.username == data['username'])
    ).first()

    if existing_user:
        return jsonify({'error': 'User with this email or username already exists'}), 400

    new_user = User(email=data['email'], username=data['username'], name=data.get('name', ''), age=data.get('age', ''))

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


@main.route('/users/<int:user_id>', methods=['PATCH'])
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


@main.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@main.route('/users', methods=['GET'])
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


@main.route('/features', methods=['POST'])
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


@main.route('/features', methods=['GET'])
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


def send_subscription_email(user, feature, is_feature_enabled):
    recipient_email = user.email
    msg = Message(subject='Wan clouds', recipients=[recipient_email])

    if is_feature_enabled:
        msg.body = f"Hello {user.username}! You have subscribed to the feature: {feature.name}"
    else:
        msg.body = f"Hello {user.username}! You don't have any features subscribed."

    mail.send(msg)


def create_subscription_job(app):
    with app.app_context():
        for subscription in Subscription.query.all():
            user = User.query.get(subscription.user_id)
            feature = Feature.query.get(subscription.feature_id)
            send_subscription_email(user, feature, subscription.is_feature_enabled)


@main.route('/subscribe', methods=['POST'])
def create_subscription():
    data = request.get_json()

    user_id = data.get('user_id')
    feature_id = data.get('feature_id')
    is_feature_enabled = data.get('feature', True)

    user = User.query.get(user_id)
    feature = Feature.query.get(feature_id)

    if not user or not feature:
        return jsonify({'error': 'User or Feature not found'}), 404

    existing_subscription = Subscription.query.filter_by(user_id=user_id, feature_id=feature_id,
                                                         is_feature_enabled=is_feature_enabled).first()

    if existing_subscription:
        return jsonify({'error': 'User is already subscribed to this feature'}), 400

    new_subscription = Subscription(user_id=user_id, feature_id=feature_id, is_feature_enabled=is_feature_enabled)
    db.session.add(new_subscription)
    db.session.commit()

    send_subscription_email(user, feature, is_feature_enabled)

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

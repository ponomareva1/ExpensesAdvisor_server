from flask import jsonify, request
from flask_restful import fields, marshal

from main import auth, users, invalid_input
from routes import user_route
from utils.fns import FNSConnector

user_fields = {
    'username': fields.String,
    'password': fields.String
}


@user_route.route('/fns/login', methods=['POST'])
@auth.login_required
def fns_login():
    fns_connector = FNSConnector()
    try:
        fns_connector.login()
    except ConnectionError:
        return jsonify({'error': "Gateway Timeout."}), 504

    return jsonify({'message': "Successfully logged in."}), 201


@user_route.route('/user/login', methods=['POST'])
def user_login():
    content = request.get_json(force=True, silent=True)
    if any(key not in content for key in ('username', 'password')):
        return invalid_input("Invalid json format (not all fields are present)")

    # request to DB
    if content['username'] not in users:
        return jsonify({'error': "Forbidden. Authorization information is invalid."}), 403
    else:
        if content['password'] != users[content['username']]:
            return jsonify({'error': "Forbidden. Authorization information is invalid."}), 403

    return jsonify({'message': "Successfully logged in."}), 201


@user_route.route('/user/registration', methods=['POST'])
def user_registration():
    content = request.get_json(force=True, silent=True)
    if any(key not in content for key in ('username', 'password')):
        return invalid_input("Invalid json format (not all fields are present)")

    # request to DB
    users[content['username']] = content['password']

    return jsonify({'message': "Successfully created account."}), 201


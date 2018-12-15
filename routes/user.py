import bcrypt
from flask import jsonify, request

from routes.common import auth, invalid_input, user_route, users
from utils.fns import FNSConnector


@user_route.route('/fns/login', methods=['POST'])
@auth.login_required
def fns_login():
    fns_connector = FNSConnector()
    try:
        fns_connector.login()
    except ConnectionError:
        return jsonify({'error': "FNS service currently unavailable."}), 503

    return jsonify({'message': "Successfully logged in."}), 201


@user_route.route('/user/login', methods=['POST'])
def user_login():
    content = request.get_json(force=True, silent=True)
    if any(key not in content for key in ('username', 'password')):
        return invalid_input("Invalid json format (not all fields are present)")

    # request to DB
    if content['username'] not in users:
        return jsonify({'error': "Forbidden. Authorization information is invalid. "
                                 "No account with this username."}), 403
    else:
        if not bcrypt.checkpw(content['password'].encode(), users.get(content['username'])):
            return jsonify({'error': "Forbidden. Invalid password."}), 403

    return jsonify({'message': "Successfully logged in."}), 201


@user_route.route('/user/registration', methods=['POST'])
def user_registration():
    content = request.get_json(force=True, silent=True)
    if any(key not in content for key in ('username', 'password')):
        return invalid_input("Invalid json format (not all fields are present)")

    # request to DB
    hashed_password = bcrypt.hashpw(content['password'].encode(), bcrypt.gensalt())
    users[content['username']] = hashed_password

    return jsonify({'message': "Successfully created account."}), 201


@user_route.route('/allUsers')
def user_all_users():
    return jsonify({'message': list(users.keys())}), 200

import bcrypt
from flask import jsonify, request

from db.DBHelper import DBHelper
from routes.common import auth, invalid_input, user_route
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
    login = content['username']
    password = content['password']

    db_helper = DBHelper()
    if not db_helper.user_exist(login):
        return jsonify({'error': "Forbidden. Authorization information is invalid. "
                                 "No account with this username."}), 403
    else:
        hashed_password = db_helper.user_password(login)
        try:
            match = bcrypt.checkpw(password.encode(), hashed_password.encode())
            if not match:
                return jsonify({'error': "Forbidden. Invalid password."}), 403
        except ValueError:
            return jsonify({'error': "Forbidden. Invalid password."}), 403

    return jsonify({'message': "Successfully logged in."}), 201


@user_route.route('/user/registration', methods=['POST'])
def user_registration():
    content = request.get_json(force=True, silent=True)
    if any(key not in content for key in ('username', 'password')):
        return invalid_input("Invalid json format (not all fields are present)")
    login = content['username']
    password = content['password']
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    db_helper = DBHelper()
    if db_helper.user_exist(login):
        return jsonify({'error': "Forbidden. An account with this username already exists."}), 406
    db_helper.add_user(login=login, password=hashed_password.decode('utf-8'))

    return jsonify({'message': "Successfully created account."}), 201


@user_route.route('/allUsers')
def user_all_users():
    db_helper = DBHelper()
    users_list = db_helper.users()
    usernames = list()
    for user in users_list:
        usernames.append(user['username'])

    return jsonify({'users': usernames}), 200


def periodic_fns_login():
    fns_connector = FNSConnector()
    try:
        fns_connector.login()
    except ConnectionError:
        return

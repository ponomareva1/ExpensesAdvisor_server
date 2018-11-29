from flask import jsonify
from flask_restful import fields, marshal

from main import auth
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
@auth.login_required
def user_login():


    return jsonify({'message': "Successfully logged in."}), 201

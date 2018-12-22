from flask import Blueprint, jsonify
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

qrcode_route = Blueprint('QRcode', __name__)
checks_route = Blueprint('checks', __name__)
items_route = Blueprint('items', __name__)
user_route = Blueprint('user', __name__)
statistics_route = Blueprint('statistics', __name__)

checks = list()
QRcodes = list()
categories = {1: "Продукты",
              2: "Услуги"}


def invalid_input(message):
    return jsonify({'error': 'Invalid input: {}'.format(message)}), 400

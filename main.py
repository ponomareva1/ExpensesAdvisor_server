from flask import Flask, make_response
from flask_httpauth import HTTPBasicAuth

from routes import *

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
auth = HTTPBasicAuth()

app.register_blueprint(qrcode_route)
app.register_blueprint(checks_route)
app.register_blueprint(items_route)

users = {
    "ponome": "ponome",
    "test": "test"
}


def invalid_input(message):
    return jsonify({'error': 'Invalid input', 'message': message}), 400


@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None


@auth.error_handler
def unauthorized():
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog
    return make_response(jsonify({'message': 'Unauthorized access'}), 401)


checks = list()
QRcodes = list()

if __name__ == '__main__':
    app.run(debug=True)

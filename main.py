import atexit
import bcrypt
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, make_response, jsonify
from flask_httpauth import HTTPBasicAuth

from routes import *

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
auth = HTTPBasicAuth()

app.register_blueprint(qrcode_route)
app.register_blueprint(checks_route)
app.register_blueprint(items_route)
app.register_blueprint(user_route)
app.register_blueprint(statistics_route)


users = {
    "ponome": bcrypt.hashpw("ponome".encode(), bcrypt.gensalt())
}


def invalid_input(message):
    return jsonify({'error': 'Invalid input', 'message': message}), 400


@auth.verify_password
def verify_password(username, password):
    if username in users:
        # get hashed password of user
        hashed = users.get(username)
        # check if received password equals to previously hashed
        return bcrypt.checkpw(password.encode(), hashed)
    else:
        return False


@auth.error_handler
def unauthorized():
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog
    return make_response(jsonify({'message': 'Unauthorized access'}), 401)


checks = list()
QRcodes = list()
categories = {1: "Продукты",
              2: "Услуги"}


def scheduled_job():
    print(datetime.now())


@app.before_first_request
def init_scheduler():
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(scheduled_job, 'interval', hours=1)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())


if __name__ == '__main__':
    app.run(use_reloader=False)

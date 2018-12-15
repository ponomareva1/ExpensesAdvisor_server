import atexit
import bcrypt
from datetime import datetime
import os
import psycopg2

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, make_response, jsonify, Blueprint
from flask_httpauth import HTTPBasicAuth

from routes import common
from routes.common import auth, users

from routes.qr_code import *
from routes.checks import *
from routes.items import *
from routes.user import *
from routes.statistics import *

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

main = Blueprint('main', __name__)


@main.route('/db')
def db():
    DATABASE_URL = os.environ['DATABASE_URL']

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    cur.execute('SELECT * FROM public."Users"')
    users = cur.fetchone()

    cur.close()
    conn.close()
    return jsonify({'message': users}), 201


@main.route('/')
def index_main():
    return jsonify({'message': "Successfully tested."}), 201


app.register_blueprint(main)
app.register_blueprint(common.qrcode_route)
app.register_blueprint(common.checks_route)
app.register_blueprint(common.items_route)
app.register_blueprint(common.user_route)
app.register_blueprint(common.statistics_route)


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

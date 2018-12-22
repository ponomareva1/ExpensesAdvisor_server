from flask import jsonify
from flask_restful import fields, marshal

from db.DBHelper import DBHelper
from routes.common import auth, statistics_route

categories_statistics_fields = {
    "category": fields.String,
    "sum": fields.Float
}

daily_statistics_fields = {
    "day": fields.DateTime(dt_format='iso8601'),
    "sum": fields.Float
}


@statistics_route.route('/statistics/categories', methods=['GET'])
@auth.login_required
def get_categories_statistics():
    db_helper = DBHelper()
    categories_statistics = db_helper.statistics_categories(auth.username())
    categories_statistics_list = list()
    for item in categories_statistics:
        marshalled_item = marshal(item, categories_statistics_fields)
        categories_statistics_list.append(marshalled_item)

    return jsonify({'statistics': categories_statistics_list}), 200


@statistics_route.route('/statistics/daily', methods=['GET'])
@auth.login_required
def get_daily_statistics():
    db_helper = DBHelper()
    daily_statistics = db_helper.statistics_daily(auth.username())
    daily_statistics_list = list()
    for item in daily_statistics:
        marshalled_item = marshal(item, daily_statistics_fields)
        daily_statistics_list.append(marshalled_item)

    return jsonify({'statistics': daily_statistics_list}), 200


from datetime import datetime

from flask import request, jsonify
from flask_restful import fields, marshal

from routes.common import auth, invalid_input, statistics_route

categories_statistics_fields = {
    "category": fields.String,
    "sum": fields.Float
}

daily_statistics_fields = {
    "day": fields.DateTime(dt_format='iso8601'),
    "sum": fields.Float
}

example_categories_statistics = {
    "statistics": [
        {
            "category": "Продукты",
            "sum": 100.2
        },
        {
            "category": "Услуги",
            "sum": 500.5
        }
    ]
}

example_daily_statistics = {
    "statistics": [
        {
            "day": datetime.strptime("2018-11-30T14:35:14", '%Y-%m-%dT%H:%M:%S'),
            "sum": 666.66
        },
        {
            "day": datetime.strptime("2018-12-31T12:00:00", '%Y-%m-%dT%H:%M:%S'),
            "sum": 42
        }
    ]
}


@statistics_route.route('/statistics/categories', methods=['GET'])
@auth.login_required
def get_categories_statistics():
    days = request.args.get('days')
    try:
        days = 30 if not days else int(days)
    except ValueError:
        return invalid_input("Parameter 'days' must be an integer")
    if not days > 0:
        return invalid_input("Parameter 'days' must be larger than 0.")

    # request to DB
    categories_statistics_list = list()
    for item in example_categories_statistics['statistics']:
        marshalled_item = marshal(item, categories_statistics_fields)
        categories_statistics_list.append(marshalled_item)

    return jsonify({'statistics': categories_statistics_list}), 200


@statistics_route.route('/statistics/daily', methods=['GET'])
@auth.login_required
def get_daily_statistics():
    days = request.args.get('days')
    try:
        days = 30 if not days else int(days)
    except ValueError:
        return invalid_input("Parameter 'days' must be an integer")
    if not days > 0:
        return invalid_input("Parameter 'days' must be larger than 0.")

    # request to DB
    daily_statistics_list = list()
    for item in example_daily_statistics['statistics']:
        marshalled_item = marshal(item, daily_statistics_fields)
        daily_statistics_list.append(marshalled_item)

    return jsonify({'statistics': daily_statistics_list}), 200


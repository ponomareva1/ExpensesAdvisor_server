from flask import jsonify
from flask_restful import fields, marshal

from main import auth, checks, invalid_input
from routes import items_route

item_fields = {
    'name': fields.String,
    'price': fields.Float,
    'quantity': fields.Float
}


@items_route.route('/items/checkID/<int:check_id>', methods=['GET'])
@auth.login_required
def get_items_from_check(check_id):
    if not check_id > 0:
        return invalid_input("Check ID must be an integer and larger than 0.")

    items = list()
    for check in checks:
        if check.id == check_id:
            items = check.items

    if not items:
        return jsonify({"error": "Check with the specified ID was not found."}), 404

    items_list = list()
    for item in items:
        marshalled_item = marshal(vars(item), item_fields)
        items_list.append(marshalled_item)

    return jsonify({'items': items_list}), 200

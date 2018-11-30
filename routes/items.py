from flask import jsonify, request
from flask_restful import fields, marshal

from main import auth, checks, invalid_input
from routes import items_route

item_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'price': fields.Float,
    'quantity': fields.Float,
    'category': fields.String
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


@items_route.route('/items/updateCategory', methods=['PUT'])
@auth.login_required
def update_items_category():
    content = request.get_json(force=True, silent=True)
    if any(key not in content for key in ('ids', 'category')):
        return invalid_input("Invalid json format (not all fields are present)")

    ids = content['ids']
    if not ids:
        return invalid_input("No ids provided.")
    category = content['category']
    if not isinstance(category, str):
        return invalid_input("Category must be a string.")

    # request to DB

    for id in ids:
        updated = False
        for check in checks:
            for item in check.items:
                if item.id == id:
                    item.category = category
                    updated = True
        if not updated:
            return jsonify({'error': "Item with the ID={} was not found.".format(id)}), 404

    return jsonify({'message': "Items category updated."}), 200

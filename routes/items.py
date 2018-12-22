from flask import jsonify, request
from flask_restful import fields, marshal

from db.DBHelper import DBHelper
from routes.common import auth, invalid_input, items_route

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

    db_helper = DBHelper()

    if not db_helper.check_exist(check_id):
        return jsonify({"error": "Check with ID={} was not found.".format(check_id)}), 404

    items = db_helper.items_info(check_id)
    items_list = list()
    for item in items:
        marshalled_item = marshal(item, item_fields)
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

    db_helper = DBHelper()
    if not db_helper.category_exist(category_name=category):
        return jsonify({'error': "Category with the name={} was not found.".format(category)}), 404
    new_category_id = db_helper.category_id(category)

    # check that all item IDs are correct
    for item_id in ids:
        if not db_helper.item_exist(item_id):
            return jsonify({'error': "Item with the ID={} was not found.".format(item_id)}), 404

    for item_id in ids:
        db_helper.update_category(item_id=item_id, new_category_id=new_category_id)

    return jsonify({'message': "Items category updated."}), 200


@items_route.route('/categories', methods=['GET'])
@auth.login_required
def get_categories():
    db_helper = DBHelper()
    categories_list = db_helper.categories()
    return jsonify({'categories': categories_list}), 200

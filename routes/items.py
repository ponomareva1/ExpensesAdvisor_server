from flask import jsonify

from main import auth
from routes import items_route


@items_route.route('/items/checkID/<int:check_id>', methods=['GET'])
@auth.login_required
def get_items_from_check(check_id):
    return jsonify({'check_id': check_id}), 200

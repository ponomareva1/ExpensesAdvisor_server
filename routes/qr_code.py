from flask import request, jsonify
from flask_restful import marshal, fields

from db.DBHelper import DBHelper
from routes.checks import check_fields
from routes.common import auth, invalid_input, qrcode_route
from shemas.shemas import QRcode
from utils.data_mapper import parse_check
from utils.fns import FNSConnector

QRcode_fields = {
    't': fields.String,
    'fn': fields.String,
    'fp': fields.String,
    'fd': fields.String,
    's': fields.String
}


@qrcode_route.route('/sendQRcode', methods=['POST'])
@auth.login_required
def send_qrcode():
    content = request.get_json(force=True, silent=True)
    if any(key not in content for key in ('t', 'fn', 'fp', 'fd', 's')):
        return invalid_input("Invalid json format (not all fields are present)")

    t = content['t']
    if 'T' not in t or len(t) not in [13, 15]:
        return invalid_input("Invalid date format")

    fn = content['fn']
    if len(fn) != 16:
        return invalid_input("Invalid 'fn' format (length != 16)")
    fp = content['fp']
    if len(fp) > 10:
        return invalid_input("Invalid 'fp' format (length > 10)")
    fd = content['fd']
    if len(fd) > 10:
        return invalid_input("Invalid 'fd' format (length > 10)")

    s = content['s']

    qrcode = QRcode(t=t, fn=fn, fp=fp, fd=fd, s=s)

    fns_connector = FNSConnector()
    db_helper = DBHelper()
    try:
        if not fns_connector.is_qrcode_correct(qrcode):
            return jsonify({'error': "Not Acceptable. Check is not found."}), 406

        check = fns_connector.get_check(qrcode)
        if check is None:
            # add json to WaitingCodes table
            json = str(vars(qrcode)).replace('\'', '\"')
            db_helper.add_waiting_code(json=json, login=auth.username())

            return jsonify({'message': "Check is not ready, added to waiting list."}), 202
    except ConnectionError:
        return jsonify({'error': "Gateway Timeout."}), 504

    check = parse_check(check)
    # add check and its items to DB
    if not db_helper.check_unique(check.specifier):
        return jsonify({'error': "Check already exist in DB."}), 406

    check.id = db_helper.add_check(specifier=check.specifier,
                                   shop=check.shop,
                                   date=check.date,
                                   login=auth.username())
    for item in check.items:
        db_helper.add_item(name=item.name, price=item.price, quant=item.quantity, check_id=check.id, category_id=1)

    return jsonify({'message': "Check added to DB.",
                    'check': marshal(vars(check), check_fields),
                    'QRcode': marshal(vars(qrcode), QRcode_fields)}), 201


def scheduled_job():
    db_helper = DBHelper()
    for waiting_code in db_helper.waiting_codes():
        json = waiting_code['json']
        qrcode = QRcode(t=json['t'], fn=json['fn'], fp=json['fp'], fd=json['fd'], s=json['s'])
        fns_connector = FNSConnector()
        db_helper = DBHelper()
        try:
            check = fns_connector.get_check(qrcode)
            if check is not None:
                check = parse_check(check)
                # add check and its items to DB
                if not db_helper.check_unique(check.specifier):
                    db_helper.delete_waiting_code(waiting_code['id'])
                    return

                username = db_helper.user_login(waiting_code['user_id'])
                check.id = db_helper.add_check(specifier=check.specifier,
                                               shop=check.shop,
                                               date=check.date,
                                               login=username)
                for item in check.items:
                    db_helper.add_item(name=item.name, price=item.price, quant=item.quantity, check_id=check.id,
                                       category_id=1)

                db_helper.delete_waiting_code(waiting_code['id'])
        except ConnectionError:
            return

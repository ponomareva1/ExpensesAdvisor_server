from flask import request, jsonify
from flask_restful import marshal, fields

from main import auth, invalid_input, checks, QRcodes
from shemas.shemas import QRcode
from utils.data_mapper import parse_check
from utils.fns import FNSConnector
from routes import qrcode_route
from routes.checks import check_fields

QRcode_fields = {
    't': fields.String,
    'fn': fields.String,
    'fp': fields.String,
    'fd': fields.String,
    's': fields.String
}


@qrcode_route.route('/sendQRcode', methods=['POST'])
@auth.login_required
def send_QRcode():
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
    QRcodes.append(qrcode)

    fns_connector = FNSConnector()
    fns_connector.login()

    if not fns_connector.is_qrcode_correct(qrcode):
        return jsonify({'error': "Not Acceptable. Check is not found."}), 406

    check = fns_connector.get_check(qrcode)
    if check is None:
        # add to waiting list
        return jsonify({'message': "Check is not ready, added to waiting list."}), 202

    check = parse_check(check)
    checks.append(check)

    return jsonify({'message': "Check added to DB.",
                    'check': marshal(vars(check), check_fields),
                    'QRcode': marshal(vars(qrcode), QRcode_fields)}), 201

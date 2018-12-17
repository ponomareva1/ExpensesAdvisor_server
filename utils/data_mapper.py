from datetime import datetime

from shemas.shemas import Check, Item


def parse_check(check_dict):
    items_list = list()
    for item in check_dict['items']:
        item_obj = Item(name=item['name'],
                        price=item['sum'] / 100,
                        quantity=item['quantity'])
        items_list.append(item_obj)

    date = datetime.strptime(check_dict['dateTime'], '%Y-%m-%dT%H:%M:%S')
    if 'retailPlace' in check_dict:
        shop = check_dict['retailPlace']
    elif 'user' in check_dict:
        shop = check_dict['user']
    else:
        shop = "Неизвестно"

    sum = float(check_dict['totalSum']) / 100

    specifier = "{fn}-{fp}-{fd}".format(fn=check_dict['fiscalDriveNumber'],
                                        fp=check_dict['fiscalSign'],
                                        fd=check_dict['fiscalDocumentNumber'])

    check = Check(date=date,
                  shop=shop,
                  sum=sum,
                  specifier=specifier,
                  items=items_list)

    return check


if __name__ == '__main__':
    from utils.fns import FNSConnector
    from shemas.shemas import QRcode

    fns_connector = FNSConnector()
    fns_connector.login()

    qrcode1 = QRcode(t="20180927T1801",
                     fn="9282000100155754",
                     fp="2472140768",
                     fd="8723",
                     s="32877")

    qrcode2 = QRcode(t="20181122T2119",
                     fn="9282000100043216",
                     fp="3013868136",
                     fd="166128",
                     s="139501")

    qrcode3 = QRcode(t="20181108T1433",
                     fn="8710000101497815",
                     fp="2592181763",
                     fd="50071",
                     s="151200")

    if fns_connector.is_qrcode_correct(qrcode1):
        json = fns_connector.get_check(qrcode1)
        print(vars(parse_check(json)))

    if fns_connector.is_qrcode_correct(qrcode2):
        json = fns_connector.get_check(qrcode2)
        print(vars(parse_check(json)))

    if fns_connector.is_qrcode_correct(qrcode3):
        json = fns_connector.get_check(qrcode3)
        print(vars(parse_check(json)))

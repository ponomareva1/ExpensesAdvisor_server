from datetime import datetime

from schemas.schemas import Check, Item


def parse_check(check_dict):
    items_list = list()
    for item in check_dict['items']:
        item_obj = Item(name=item['name'].replace('\'', '`'),
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
    shop = shop.replace('\'', '`')

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
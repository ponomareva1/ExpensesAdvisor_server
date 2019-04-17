import os
from datetime import date, datetime, timedelta

import pytest
import testing.postgresql
import psycopg2 as pg

from db.DBHelper import DBHelper


def handler(postgresql):
    connection = pg.connect(**postgresql.dsn())
    cursor = connection.cursor()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    script_path = os.path.join(project_root, 'db', 'scripts', 'WHOLE_DB_CREATE.sql')
    sql_file = open(script_path, 'r')
    cursor.execute(sql_file.read())
    cursor.close()
    connection.commit()
    connection.close()


Postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True,
                                                  on_initialized=handler)


def get_helper(params):
    return DBHelper(remote=False, connect_params=params)


@pytest.fixture
def postgresql():
    postgresql = Postgresql()
    yield postgresql
    postgresql.stop()


#
# Query tests
#
def test_query_Positive_TableCreated(postgresql):
    helper = get_helper(params=postgresql.dsn())
    helper.query(query="CREATE TABLE test (num integer, data varchar);")

    expected_table_present = 'test'

    connection = pg.connect(**postgresql.dsn())
    cursor = connection.cursor()
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    actual_tables = cursor.fetchall()
    actual_tables = [table[0] for table in actual_tables]

    assert expected_table_present in actual_tables

    cursor.close()
    connection.close()


def test_query_Negative_InvalidQueryReturnsNone(postgresql):
    helper = get_helper(params=postgresql.dsn())
    assert helper.query(query="fail") is None


#
# Users tests
#
def test_add_user_Positive_UserAdded(postgresql):
    helper = get_helper(params=postgresql.dsn())

    expected_user = {
        'id': 1,
        'username': 'user',
        'password': 'pass'
    }

    helper.add_user(login=expected_user['username'], password=expected_user['password'])

    user = helper.query(query="SELECT * FROM \"Users\";")[0]
    fields = ['id', 'username', 'password']
    actual_user = dict(zip(fields, user))

    assert actual_user == expected_user


def test_users_Positive_OneUserExists(postgresql):
    helper = get_helper(params=postgresql.dsn())

    expected_user = {
        'id': 1,
        'username': 'user',
        'password': 'pass'
    }

    helper.add_user(login=expected_user['username'], password=expected_user['password'])
    actual_user = helper.users()[0]

    assert actual_user == expected_user


def test_users_Negative_UsersNotExist(postgresql):
    helper = get_helper(params=postgresql.dsn())
    assert helper.users() is None


def test_user_login_Positive_GetExistingUserLogin(postgresql):
    helper = get_helper(params=postgresql.dsn())

    expected_user_login = 'user'
    actual_user_id = helper.add_user(login=expected_user_login, password='pass')

    actual_user_login = helper.user_login(user_id=actual_user_id)

    assert actual_user_login == expected_user_login


def test_user_login_Negative_UserNotExists(postgresql):
    helper = get_helper(params=postgresql.dsn())
    assert helper.user_login(user_id=1) is None


def test_user_password_Positive_GetExistingUserPassword(postgresql):
    helper = get_helper(params=postgresql.dsn())

    expected_user_login = 'user'
    expected_user_password = 'pass'
    helper.add_user(login=expected_user_login, password=expected_user_password)

    actual_user_password = helper.user_password(login=expected_user_login)

    assert actual_user_password == expected_user_password


def test_user_password_Negative_UserNotExists(postgresql):
    helper = get_helper(params=postgresql.dsn())
    assert helper.user_password(login='login') is None


def test_user_id_Positive_GetExistingUserID(postgresql):
    helper = get_helper(params=postgresql.dsn())

    expected_user_login = 'user'
    expected_user_password = 'pass'
    expected_user_id = helper.add_user(login=expected_user_login, password=expected_user_password)

    actual_user_id = helper.user_id(login=expected_user_login)

    assert actual_user_id == expected_user_id


def test_user_id_Negative_UserNotExists(postgresql):
    helper = get_helper(params=postgresql.dsn())
    assert helper.user_id(login='login') is None


def test_user_exist_Positive_UserExists(postgresql):
    helper = get_helper(params=postgresql.dsn())

    expected_user_login = 'user'
    helper.add_user(login=expected_user_login, password='pass')

    actual_user_exists = helper.user_exist(login=expected_user_login)

    assert actual_user_exists


def test_user_exist_Negative_UserNotExists(postgresql):
    helper = get_helper(params=postgresql.dsn())
    assert not helper.user_exist(login='login')


#
# Checks tests
#
def test_add_check_Positive_CheckAdded(postgresql):
    helper = get_helper(params=postgresql.dsn())

    user_login = 'user'
    user_id = helper.add_user(login=user_login, password='pass')

    expected_check = {
        'id': 1,
        'specifier': 'specifier',
        'shop': 'shop',
        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'user_id': user_id
    }

    helper.add_check(specifier=expected_check['specifier'],
                     shop=expected_check['shop'],
                     date=expected_check['date'],
                     login=user_login)

    check = helper.query(query="SELECT * FROM \"Checks\"")[0]
    fields = ['id', 'specifier', 'shop', 'date', 'user_id']
    actual_check = dict(zip(fields, check))
    actual_check['date'] = actual_check['date'].strftime("%Y-%m-%d %H:%M")

    assert actual_check == expected_check


def test_get_last_checks_Positive_GetOneLastFromTwoPresent(postgresql):
    helper = get_helper(params=postgresql.dsn())

    user_login = 'user'
    helper.add_user(login=user_login, password='pass')

    category_id = helper.add_category(name='category')

    expected_sum = 100
    expected_check = {
        'shop': 'shop',
        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'sum': expected_sum
    }

    expected_check_id = helper.add_check(specifier='specifier',
                                         shop=expected_check['shop'],
                                         date=expected_check['date'],
                                         login=user_login)

    expected_check['id'] = expected_check_id

    helper.add_item(name='name1', price=expected_sum, quant=1, check_id=expected_check['id'], category_id=category_id)

    earlier_date = datetime.now() - timedelta(days=1)
    additional_check = {
        'specifier': 'specifier2',
        'shop': 'shop2',
        'date': earlier_date.strftime("%Y-%m-%d %H:%M"),
        'sum': 200
    }

    additional_check_id = helper.add_check(specifier=additional_check['specifier'],
                                           shop=additional_check['shop'],
                                           date=additional_check['date'],
                                           login=user_login)

    helper.add_item(name='name2', price=200, quant=1, check_id=additional_check_id, category_id=category_id)

    actual_check = helper.get_last_checks(limit=1, login=user_login)[0]
    actual_check['sum'] = float(actual_check['sum'])
    actual_check['date'] = actual_check['date'].strftime("%Y-%m-%d %H:%M")

    assert actual_check == expected_check


def test_get_last_checks_Negative_ChecksNotExist(postgresql):
    helper = get_helper(params=postgresql.dsn())
    assert helper.get_last_checks(limit=1, login='login') is None


def test_check_id_Positive_GetExistingCheckId(postgresql):
    helper = get_helper(params=postgresql.dsn())

    check = {
        'specifier': 'specifier',
        'shop': 'shop',
        'date': datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    user_login = 'user'

    expected_check_id = helper.add_check(specifier=check['specifier'],
                                         shop=check['shop'],
                                         date=check['date'],
                                         login=user_login)

    actual_check_id = helper.check_id(specifier=check['specifier'])

    assert actual_check_id == expected_check_id


def test_check_id_Negative_ChecksNotExist(postgresql):
    helper = get_helper(params=postgresql.dsn())
    assert helper.check_id(specifier='specifier') is None


def test_check_exist_Positive_CheckExists(postgresql):
    helper = get_helper(params=postgresql.dsn())

    check = {
        'specifier': 'specifier',
        'shop': 'shop',
        'date': datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    user_login = 'user'
    helper.add_user(login=user_login, password='pass')

    expected_check_id = helper.add_check(specifier=check['specifier'],
                                         shop=check['shop'],
                                         date=check['date'],
                                         login=user_login)

    actual_check_exists = helper.check_exist(check_id=expected_check_id)

    assert actual_check_exists


def test_check_exist_Negative_CheckNotExists(postgresql):
    helper = get_helper(params=postgresql.dsn())
    assert not helper.check_exist(check_id=1)


def test_check_unique_Positive_SpecifierIsUnique(postgresql):
    helper = get_helper(params=postgresql.dsn())
    assert helper.check_unique(specifier='specifier')


def test_check_unique_Positive_SpecifierIsNotUnique(postgresql):
    helper = get_helper(params=postgresql.dsn())

    check = {
        'specifier': 'specifier',
        'shop': 'shop',
        'date': datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    user_login = 'user'
    helper.add_user(login=user_login, password='pass')

    helper.add_check(specifier=check['specifier'],
                     shop=check['shop'],
                     date=check['date'],
                     login=user_login)

    actual_check_unique = helper.check_unique(specifier=check['specifier'])

    assert not actual_check_unique


#
# Items tests
#
def test_add_item_Positive_ItemAdded(postgresql):
    helper = get_helper(params=postgresql.dsn())

    expected_item = {
        'name': 'name',
        'price': 100,
        'quantity': 1
    }
    user_login = 'user'

    helper.add_user(login=user_login, password='pass')
    expected_item['category_id'] = helper.add_category(name='category')
    expected_item['check_id'] = helper.add_check(specifier='specifier', shop='shop', date=datetime.now(),
                                                 login=user_login)

    expected_item['id'] = helper.add_item(name=expected_item['name'],
                                          price=expected_item['price'],
                                          quant=expected_item['quantity'],
                                          check_id=expected_item['check_id'],
                                          category_id=expected_item['category_id'])

    item = helper.query(query="SELECT * FROM \"Items\"")[0]
    fields = ['id', 'name', 'price', 'quantity', 'check_id', 'category_id']
    actual_item = dict(zip(fields, item))
    actual_item['price'] = float(actual_item['price'])

    assert actual_item == expected_item


def test_items_info_Positive_InfoForExistingItem(postgresql):
    helper = get_helper(params=postgresql.dsn())

    expected_item = {
        'name': 'name',
        'price': 100,
        'quantity': 1,
        'category': 'category'
    }
    user_login = 'user'

    helper.add_user(login=user_login, password='pass')
    category_id = helper.add_category(name=expected_item['category'])
    check_id = helper.add_check(specifier='specifier', shop='shop', date=datetime.now(), login=user_login)

    expected_item['id'] = helper.add_item(name=expected_item['name'],
                                          price=expected_item['price'],
                                          quant=expected_item['quantity'],
                                          check_id=check_id,
                                          category_id=category_id)

    actual_item = helper.items_info(check_id=check_id)[0]

    assert actual_item == expected_item


def test_items_info_Negative_ItemsNotExist(postgresql):
    helper = get_helper(params=postgresql.dsn())
    assert helper.items_info(check_id=1) is None


def test_item_id_Positive_GetExistingItemId(postgresql):
    helper = get_helper(params=postgresql.dsn())

    item = {
        'name': 'name',
        'price': 100,
        'quantity': 1,
    }
    user_login = 'user'

    helper.add_user(login=user_login, password='pass')
    category_id = helper.add_category(name='category')
    check_id = helper.add_check(specifier='specifier', shop='shop', date=datetime.now(), login=user_login)

    expected_item_id = helper.add_item(name=item['name'],
                                       price=item['price'],
                                       quant=item['quantity'],
                                       check_id=check_id,
                                       category_id=category_id)

    actual_item_id = helper.item_id(name=item['name'], check_id=check_id)

    assert actual_item_id == expected_item_id


def test_item_id_Negative_ItemNotExists(postgresql):
    helper = get_helper(params=postgresql.dsn())
    assert helper.item_id(name='name', check_id=1) is None


def test_item_exist_Positive_ItemExists(postgresql):
    helper = get_helper(params=postgresql.dsn())

    item = {
        'name': 'name',
        'price': 100,
        'quantity': 1
    }
    user_login = 'user'

    helper.add_user(login=user_login, password='pass')
    category_id = helper.add_category(name='category')
    check_id = helper.add_check(specifier='specifier', shop='shop', date=datetime.now(), login=user_login)

    item['id'] = helper.add_item(name=item['name'],
                                 price=item['price'],
                                 quant=item['quantity'],
                                 check_id=check_id,
                                 category_id=category_id)

    actual_item_exists = helper.item_exist(item_id=item['id'])

    assert actual_item_exists


def test_item_exist_Negative_ItemNotExists(postgresql):
    helper = get_helper(params=postgresql.dsn())
    assert not helper.item_exist(item_id=1)


#
# Categories tests
#
def test_add_category_Positive_CategoryAdded(postgresql):
    helper = get_helper(params=postgresql.dsn())

    expected_category = {
        'id': 1,
        'name': 'category'
    }

    helper.add_category(name=expected_category['name'])

    category = helper.query(query="SELECT * FROM \"Categories\";")[0]
    fields = ['id', 'name']
    actual_category = dict(zip(fields, category))

    assert actual_category == expected_category


def test_update_category_Positive_CategoryUpdated(postgresql):
    helper = get_helper(params=postgresql.dsn())

    old_category_id = helper.add_category(name='old_category')
    expected_new_category_id = helper.add_category(name='new_category')

    helper.add_user(login='user', password='pass')
    check_id = helper.add_check(specifier='specifier', shop='shop', date=datetime.now(), login='user')
    item_id = helper.add_item(name='name', price=100, quant=1, check_id=check_id, category_id=old_category_id)

    helper.update_category(item_id=item_id, new_category_id=expected_new_category_id)

    actual_category_id = helper.query(query="SELECT id_category FROM \"Items\" WHERE id = {item_id}".
                                      format(item_id=item_id))[0][0]

    assert actual_category_id == expected_new_category_id


def test_update_category_Negative_CategoryNotExistsItemNotUpdated(postgresql):
    helper = get_helper(params=postgresql.dsn())

    category_id = helper.add_category(name='old_category')

    helper.add_user(login='user', password='pass')
    check_id = helper.add_check(specifier='specifier', shop='shop', date=datetime.now(), login='user')
    item_id = helper.add_item(name='name', price=100, quant=1, check_id=check_id, category_id=category_id)

    helper.update_category(item_id=item_id, new_category_id=1)

    actual_category_id = helper.query(query="SELECT id_category FROM \"Items\" WHERE id = {item_id}".
                                      format(item_id=item_id))[0][0]

    assert actual_category_id == category_id


def test_category_id_Positive_GetExistingCategoryId(postgresql):
    helper = get_helper(params=postgresql.dsn())

    category_name = 'category'
    expected_category_id = helper.add_category(name=category_name)

    actual_category_id = helper.category_id(name=category_name)

    assert actual_category_id == expected_category_id


def test_category_id_Negative_CategoryNotExists(postgresql):
    helper = get_helper(params=postgresql.dsn())
    assert helper.category_id(name='category') is None


def test_categories_Positive_TwoExistingCategories(postgresql):
    helper = get_helper(params=postgresql.dsn())

    expected_categories = ['category1', 'category2']
    helper.add_category(name=expected_categories[0])
    helper.add_category(name=expected_categories[1])

    actual_categories = helper.categories()

    assert actual_categories == expected_categories


def test_categories_Negative_CategoriesNotExist(postgresql):
    helper = get_helper(params=postgresql.dsn())
    assert helper.categories() is None


def test_category_exist_Positive_CategoryExists(postgresql):
    helper = get_helper(params=postgresql.dsn())

    category_name = 'category'
    helper.add_category(name=category_name)

    actual_category_exists = helper.category_exist(name=category_name)

    assert actual_category_exists


def test_category_exist_Positive_CategoryNotExists(postgresql):
    helper = get_helper(params=postgresql.dsn())
    assert not helper.category_exist(name='category')


#
# WaitingCodes tests
#
def test_add_waiting_code_Positive_WaitingCodeAdded(postgresql):
    helper = get_helper(params=postgresql.dsn())

    user_login = 'user'
    user_id = helper.add_user(login=user_login, password='pass')
    expected_waiting_code = {
        'id': 1,
        'user_id': user_id,
        'json': {'key1': 'val1'},
    }
    helper.add_waiting_code(login=user_login, json=str(expected_waiting_code['json']).replace('\'', '\"'))

    waiting_code = helper.query(query="SELECT * FROM \"WaitingCodes\";")[0]
    fields = ['user_id', 'json', 'id']
    actual_waiting_code = dict(zip(fields, waiting_code))

    assert actual_waiting_code == expected_waiting_code


def test_waiting_codes_Positive_TwoExistingWaitingCodes(postgresql):
    helper = get_helper(params=postgresql.dsn())

    user_id = helper.add_user(login='user', password='pass')

    expected_first_code = {
        'id': 1,
        'user_id': user_id,
        'json': {'key1': 'val1'},
    }
    expected_second_code = {
        'id': 2,
        'user_id': user_id,
        'json': {'key2': 'val2'},
    }

    helper.add_waiting_code(login='user', json=str(expected_first_code['json']).replace('\'', '\"'))
    helper.add_waiting_code(login='user', json=str(expected_second_code['json']).replace('\'', '\"'))

    actual_waiting_codes = helper.waiting_codes()

    assert actual_waiting_codes == [expected_first_code, expected_second_code]


def test_waiting_codes_Negative_WaitingCodesNotExist(postgresql):
    helper = get_helper(params=postgresql.dsn())
    assert helper.waiting_codes() is None


def test_delete_waiting_code_Positive_DeleteExistingCategoryOneLeft(postgresql):
    helper = get_helper(params=postgresql.dsn())

    user_id = helper.add_user(login='user', password='pass')

    expected_first_code = {
        'id': 1,
        'user_id': user_id,
        'json': {'key1': 'val1'},
    }
    expected_second_code = {
        'id': 2,
        'user_id': user_id,
        'json': {'key2': 'val2'},
    }

    helper.add_waiting_code(login='user', json=str(expected_first_code['json']).replace('\'', '\"'))
    helper.add_waiting_code(login='user', json=str(expected_second_code['json']).replace('\'', '\"'))

    actual_waiting_codes = helper.waiting_codes()

    assert actual_waiting_codes == [expected_first_code, expected_second_code]

    helper.delete_waiting_code(id=expected_second_code['id'])

    actual_waiting_codes = helper.waiting_codes()

    assert actual_waiting_codes == [expected_first_code]


def test_delete_waiting_code_Negative_DeleteNotExistingCategoryOneLeft(postgresql):
    helper = get_helper(params=postgresql.dsn())

    user_id = helper.add_user(login='user', password='pass')

    expected_waiting_code = {
        'id': 1,
        'user_id': user_id,
        'json': {'key1': 'val1'},
    }
    helper.add_waiting_code(login='user', json=str(expected_waiting_code['json']).replace('\'', '\"'))

    actual_waiting_codes = helper.waiting_codes()

    assert actual_waiting_codes == [expected_waiting_code]

    helper.delete_waiting_code(id=100)

    actual_waiting_codes = helper.waiting_codes()

    assert actual_waiting_codes == [expected_waiting_code]


#
# Statistics tests
#
def test_statistics_categories_Positive_GetStatistics(postgresql):
    helper = get_helper(params=postgresql.dsn())

    user = 'user'
    helper.add_user(login=user, password='pass')
    helper.add_category(name='category1')
    helper.add_category(name='category2')
    helper.add_check(specifier='spec', shop='shop', date=datetime.now(), login=user)
    helper.add_item(name='item1', price=1, quant=1, check_id=1, category_id=1)
    helper.add_item(name='item2', price=2, quant=2, check_id=1, category_id=2)

    expected_statistics = [
        {
            'category': 'category1',
            'sum': 1
        },
        {
            'category': 'category2',
            'sum': 2
        }
    ]

    actual_statistics = helper.statistics_categories(login=user)

    assert actual_statistics == expected_statistics


def test_statistics_categories_Negative_UserNotExists(postgresql):
    helper = get_helper(params=postgresql.dsn())
    assert helper.statistics_categories(login='login') is None


def test_statistics_daily_Positive_GetStatistics(postgresql):
    helper = get_helper(params=postgresql.dsn())

    user = 'user'
    helper.add_user(login=user, password='pass')
    helper.add_category(name='category1')
    helper.add_category(name='category2')
    helper.add_check(specifier='spec', shop='shop', date=datetime.now(), login=user)
    helper.add_item(name='item1', price=1, quant=1, check_id=1, category_id=1)
    helper.add_item(name='item2', price=2, quant=2, check_id=1, category_id=2)

    numdays = 10
    base = date.today()
    expected_statistics = [{'day': base - timedelta(days=x), 'sum': 0} for x in range(numdays, -2, -1)]
    expected_statistics[-2]['sum'] = 3

    actual_statistics = helper.statistics_daily(user)

    assert actual_statistics == expected_statistics


def test_statistics_daily_Negative_UserNotExists(postgresql):
    helper = get_helper(params=postgresql.dsn())
    assert helper.statistics_daily(login='login') is None

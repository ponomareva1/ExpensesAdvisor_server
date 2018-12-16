import unittest
from db.DBHelper import DBHelper
from datetime import datetime


class DBHelperTest(unittest.TestCase):

    def setUp(self):
        self.db = DBHelper()
        self.delete_category_pattern = """DELETE FROM "Categories" WHERE name = '{}'"""
        self.delete_user_pattern = """DELETE FROM "Users" WHERE login = '{l}' AND password = '{p}'"""
        self.check_exists_pattern = """SELECT CASE WHEN EXISTS ({select_query}) THEN True ELSE False END"""

    # USER API Tests
    def test_add_user(self):
        login = datetime.now().__str__()
        password = login
        check_query = self.check_exists_pattern.format(select_query="""SELECT * FROM "Users" 
                                                                       WHERE login = '{l}' 
                                                                       AND password = '{p}'""".format(l=login,
                                                                                                      p=password))
        delete_query = self.delete_user_pattern.format(l=login, p=password)
        self.db.add_user(login, password)
        self.assertEqual(True, self.db.db.query(check_query)[0][0])
        self.db.db.query(delete_query)

    def test_user_exist(self):
        login = datetime.now().__str__()
        password = login
        delete_query = self.delete_user_pattern.format(l=login, p=password)
        self.db.add_user(login, password)
        self.assertEqual(True, self.db.user_exist(login))
        self.db.db.query(delete_query)

    def test_users(self):
        login = datetime.now().__str__()
        password = login
        delete_query = self.delete_user_pattern.format(l=login, p=password)
        self.db.add_user(login, password)
        self.assertGreater(len(self.db.users()), 0)
        self.db.db.query(delete_query)

    # CATEGORY API Tests
    def test_add_category(self):
        name = datetime.now().__str__()
        self.db.add_category(name)
        check_query = self.check_exists_pattern.format(select_query="""SELECT * FROM "Categories"
                                                                       WHERE name = '{}'""".format(name))
        self.assertEqual(True, self.db.db.query(check_query)[0][0])
        delete_query = self.delete_category_pattern.format(name)
        self.db.db.query(delete_query)

    def test_categories(self):
        name = datetime.now().__str__()
        delete_query = self.delete_category_pattern.format(name)
        self.db.add_category(name)
        self.assertGreater(len(self.db.categories()), 0)
        self.db.db.query(delete_query)

    # def test_update_category(self):

    # CHECKS API tests
    def test_add_check(self):
        tmp = datetime.now().__str__()
        check_query = self.check_exists_pattern.format(select_query="""SELECT * FROM "Checks"
                                                                       WHERE specifier = '{}'""".format(tmp))
        self.db.add_user(tmp, tmp)
        user_id = self.db.user_id(tmp)
        self.db.add_check(tmp, tmp, tmp, user_id)
        self.assertEqual(True, self.db.db.query(check_query)[0][0])
        delete_user_query = self.delete_user_pattern.format(l=tmp, p=tmp)  # cascade deleting
        self.db.db.query(delete_user_query)

    def test_get_last_checks(self):
        n = 5
        login = datetime.now().__str__()
        self.db.add_user(login, login)
        user_id = self.db.user_id(login)
        for i in range(n):
            tmp = datetime.now().__str__()
            self.db.add_check(tmp, tmp, tmp, user_id)
        result = self.db.get_last_checks(n, login)
        self.assertEqual(len(result), n)
        delete_user_query = self.delete_user_pattern.format(l=login, p=login)  # cascade deleting
        self.db.db.query(delete_user_query)


if __name__ == '__main__':
    unittest.main()

import unittest
from db.DBHelper import DBHelper
from datetime import datetime


class DBHelperTest(unittest.TestCase):

    def setUp(self):
        self.db = DBHelper()

    # USER API Tests
    def test_add_user(self):
        login = datetime.now().__str__()
        password = login
        check_query = """SELECT CASE WHEN EXISTS (
                                SELECT *
                                FROM "Users"
                                WHERE login = '%s' AND password = '%s'
                            )
                            THEN True
                            ELSE False END""" % (login, password)
        delete_query = """DELETE FROM "Users" WHERE login = '%s' AND password = '%s'""" % (login, password)
        self.db.add_user(login, password)
        self.assertEqual(True, self.db.db.query(check_query)[0][0])
        self.db.db.query(delete_query)

    def test_user_exist(self):
        login = datetime.now().__str__()
        password = login
        delete_query = """DELETE FROM "Users" WHERE login = '%s' AND password = '%s'""" % (login, password)
        self.db.add_user(login, password)
        self.assertEqual(True, self.db.user_exist(login))
        self.db.db.query(delete_query)

    def test_users(self):
        login = datetime.now().__str__()
        password = login
        delete_query = """DELETE FROM "Users" WHERE login = '%s' AND password = '%s'""" % (login, password)
        self.db.add_user(login, password)
        self.assertGreater(len(self.db.users()), 0)
        self.db.db.query(delete_query)

    # CATEGORY API Tests
    def test_add_category(self):
        name = datetime.now().__str__()
        self.db.add_category(name)
        check_query = """SELECT CASE WHEN EXISTS (
                                        SELECT *
                                        FROM "Categories"
                                        WHERE name = '%s'
                                    )
                                    THEN True
                                    ELSE False END""" % name
        self.assertEquals(True, self.db.db.query(check_query)[0][0])
        delete_query = """DELETE FROM "Categories" WHERE name = '%s'""" % name
        self.db.db.query(delete_query)

    def test_categories(self):
        name = datetime.now().__str__()
        delete_query = """DELETE FROM "Categories" WHERE name = '%s'""" % name
        self.db.add_category(name)
        self.assertGreater(len(self.db.categories()), 0)
        self.db.db.query(delete_query)

    # CHECKS API tests
    def test_add_check(self):
        tmp = datetime.now().__str__()
        check_query = """SELECT CASE WHEN EXISTS (
                                                SELECT *
                                                FROM "Checks"
                                                WHERE specifier = '%s'
                                            )
                                            THEN True
                                            ELSE False END""" % tmp
        self.db.add_user(tmp, tmp)
        self.db.add_check(tmp, tmp, tmp, tmp)
        self.assertEquals(True, self.db.db.query(check_query)[0][0])
        delete_user_query = """DELETE FROM "Users" WHERE login = '%s'""" % tmp  # cascade deleting
        self.db.db.query(delete_user_query)

    def test_get_last_checks(self):
        n = 5
        user_tmp = datetime.now().__str__()
        self.db.add_user(user_tmp, user_tmp)
        for i in range(n):
            tmp = datetime.now().__str__()
            self.db.add_check(tmp, tmp, tmp, user_tmp)
        result = self.db.get_last_checks(n, user_tmp)
        self.assertEqual(len(result), n)
        delete_user_query = """DELETE FROM "Users" WHERE login = '%s'""" % user_tmp  # cascade deleting
        self.db.db.query(delete_user_query)


if __name__ == '__main__':
    unittest.main()

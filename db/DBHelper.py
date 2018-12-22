import logging
import os

import psycopg2 as pg
from db.DBConstants import *

# TODO: methods for statistic

logger = logging.getLogger(__name__)


class DBHelper:

    def __init__(self, remote=True, user=USER, password=PASS, host=HOST, port=PORT, db_name=DB_NAME):
        try:
            if remote:
                database_url = os.environ['DATABASE_URL']
                self.connection = pg.connect(database_url, sslmode='require')
            else:
                self.connection = self.__connect(user, password, host, port, db_name)
        except Exception as e:
            logger.error("CONNECTION ERROR:")
            logger.error(e)

    def close_connection(self):
        self.connection.close()

    #
    # User API
    #
    def users(self):
        users = self.__select_all_query(USERS_TABLE)
        fields = ['id', 'username', 'password']
        return [dict(zip(fields, user)) for user in users]

    def add_user(self, login, password):
        values = "('{login}','{password}')".format(login=login, password=password)
        self.__insert_query(USERS_TABLE, "(login,password)", values)
        return self.user_id(login)

    def user_exist(self, login):
        query = """SELECT CASE WHEN EXISTS (
                                        SELECT *
                                        FROM {USERS_TABLE}
                                        WHERE login = '{login}'
                        )
                        THEN True
                        ELSE False END""".format(USERS_TABLE=USERS_TABLE, login=login)
        return self.query(query)[0][0]

    def user_password(self, login):
        return self.__select_query("password", USERS_TABLE, "WHERE login = '{}'".format(login))[0][0]

    def user_id(self, login):
        return self.__select_query("id", USERS_TABLE, "WHERE login = '{}'".format(login))[0][0]

    #
    # Checks API
    #
    def checks(self):
        return self.__select_all_query(CHECKS_TABLE)

    def add_check(self, specifier, shop, date, login):
        user_id = self.user_id(login)
        self.__insert_query(CHECKS_TABLE,
                            "(specifier,shop,date,id_user)",
                            "('{specifier}','{shop}','{date}',{user_id})".format(specifier=specifier, shop=shop,
                                                                                 date=date, user_id=user_id))
        return self.check_id(specifier)

    def get_last_checks(self, limit, login):
        user_id = self.user_id(login)
        columns = "ch.id, ch.shop, ch.date, ch.id_user, sum(i.price) as sum"
        tables = "{CHECKS_TABLE} ch JOIN {ITEMS_TABLE} i ON ch.id = i.id_check".format(ITEMS_TABLE=ITEMS_TABLE,
                                                                                       CHECKS_TABLE=CHECKS_TABLE)
        constraint = """WHERE ch.id_user = {user_id}
                        GROUP BY ch.id, ch.shop, ch.date, ch.id_user
                        LIMIT {limit}
                        """.format(user_id=user_id, limit=limit)
        checks = self.__select_query(columns, tables, constraint)

        fields = ['id', 'shop', 'date', 'user_id', 'sum']
        return [dict(zip(fields, check)) for check in checks]

    def check_id(self, specifier):
        return self.__select_query("id", CHECKS_TABLE, "WHERE specifier = '{}'".format(specifier))[0][0]

    #
    # Items API
    #
    def items_info(self, check_id):
        columns = "i.name,price,quant,c.name AS category"
        tables = """{ITEMS_TABLE} i JOIN {CHECKS_TABLE} ch ON ch.id = i.id_check 
                                    JOIN {CATEGORIES_TABLE} c ON c.id = i.id_category""". \
            format(ITEMS_TABLE=ITEMS_TABLE,
                   CHECKS_TABLE=CHECKS_TABLE,
                   CATEGORIES_TABLE=CATEGORIES_TABLE)
        constraint = "WHERE ch.id = {id}".format(id=check_id)
        return self.__select_query(columns, tables, constraint)

    def items_sum(self, check_id):
        return self.__select_query("sum(price)", ITEMS_TABLE,
                                   "WHERE id_check = {check_id}".format(check_id=check_id))[0][0]

    # TODO: test for method
    def add_item(self, name, price, quant, check_id, category_id):
        self.__insert_query(ITEMS_TABLE, "(name,price,quant,id_category,id_check)",
                            "('{name}',{price},{quant},{category_id},{check_id})".format(name=name, price=price,
                                                                                         quant=quant, check_id=check_id,
                                                                                         category_id=category_id))
        return self.item_id(name, check_id)

    def item_id(self, name, check_id):
        return self.__select_query("id", ITEMS_TABLE, "WHERE name = '{name}' "
                                                      "AND id_check = {check_id}".format(name=name,
                                                                                         check_id=check_id))[0][0]

    #
    # Category API
    #
    def update_category(self, check_id, item_id, new_category_id):
        # TODO + QUATION: update all such items or only item in this check ???
        constraint = """WHERE id_check = {check_id} AND id = {item_id}""".format(check_id=check_id, item_id=item_id)
        self.__update_query(ITEMS_TABLE, "id_category = {} ".format(new_category_id), constraint)

    def category_id(self, name):
        return self.__select_query("id", CATEGORIES_TABLE, "WHERE name = '{name}'".format(name=name))[0][0]

    def categories(self):
        categories = self.__select_all_query(CATEGORIES_TABLE)

        categories_list = list()
        for category in categories:
            categories_list.append(category[1])

        return categories_list

    def add_category(self, name):
        self.__insert_query(CATEGORIES_TABLE, "(name)", "('{}')".format(name))
        return self.category_id(name)

    #
    # WaitingCodes API
    #
    def waiting_codes(self):
        return self.__select_all_query(WAITING_CHECKS_TABLE)

    def add_waiting_code(self, login, json):
        user_id = self.user_id(login)
        self.__insert_query(WAITING_CHECKS_TABLE,
                            "(json,id_user)",
                            "('{json}',{user_id})".format(json=json, user_id=user_id))
        return self.check_id(json)

    def waiting_code_id(self, json):
        return self.__select_query("id", WAITING_CHECKS_TABLE, "WHERE json = '{}'".format(json))[0][0]

    #
    # Queries
    #
    @staticmethod
    def __connect(user, password, host, port, db_name):
        return pg.connect(
            "dbname='{db_name}' user='{user}' host='{host}' password='{passw}'".format(db_name=db_name,
                                                                                       user=user,
                                                                                       passw=password,
                                                                                       host=host))

    def query(self, query):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            rows = cursor.fetchall() if cursor.description is not None else None
            self.connection.commit()
            cursor.close()
            return rows
        except Exception as e:
            self.connection.rollback()
            cursor.close()
            logger.warn("Error with query : {}".format(query))
            logger.warn(e)

    def __query_with_args(self, command, table_name, constraint=""):
        query = command + " " + table_name + " " + constraint
        return self.query(query)

    def __update_query(self, table_name, set, constraint=""):
        self.__query_with_args("UPDATE", table_name, " SET " + set + " " + constraint)

    def __insert_query(self, table_name, where, what):
        self.__query_with_args("INSERT INTO", table_name, where + " VALUES " + what)

    def __select_query(self, columns, table_name, constraint=""):
        return self.__query_with_args("SELECT {columns} FROM ".format(columns=columns), table_name, constraint)

    # def __select_top_query(self, n, table_name, columns="*", constraint=""):
    #     return self.__select_query(columns, table_name, constraint + "LIMIT {}".format(n))

    def __select_all_query(self, table_name, constraint=""):
        return self.__select_query("*", table_name, constraint)
import logging
import os

import psycopg2 as pg
from os import listdir
from db.date.ItemInfo import *
from db.DBConstants import *

# TODO: methods for statistic
# TODO: methods for waiting chacks

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

    #
    # User API
    #
    def users(self):
        return self.__select_all_query(USERS_TABLE)

    def add_user(self, login, password):
        # TODO: login&pass checking

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

    def user_id(self, login):
        return self.__select_query("id", USERS_TABLE, "WHERE login = '{}'".format(login))[0][0]

    #
    # Checks API
    #
    def checks(self):
        return self.__select_all_query(CHECKS_TABLE)

    def add_check(self, specifier, shop, date, user_id):
        self.__insert_query(CHECKS_TABLE,
                            "(specifier,shop,date,id_user)",
                            "('{specifier}','{shop}','{date}',{user_id})".format(specifier=specifier, shop=shop,
                                                                                 date=date, user_id=user_id))
        return self.check_id(specifier)

    def get_last_checks(self, n, login):
        if not self.user_exist(login):
            raise Exception("User with login '{}' doesn't exist".format(login))
        user_id = self.user_id(login)
        return self.__select_top_query(n, CHECKS_TABLE, constraint="WHERE id_user = {}".format(user_id))

    def check_id(self, specifier):
        return self.__select_query("id", CHECKS_TABLE, "WHERE specifier = '{}'".format(specifier))[0][0]

    #
    # Items API
    #
    def items_info(self, check_id):
        columns = "i.name,price,quant,c.name AS category"
        tables = """{ITEMS_TABLE} i JOIN {CHECKS_TABLE} ch ON ch.id = i.id_check 
                                    JOIN {CATEGORIES_TABLE} c ON c.id = i.id_category""".format(ITEMS_TABLE=ITEMS_TABLE,
                                                                                                CHECKS_TABLE=CHECKS_TABLE,
                                                                                                CATEGORIES_TABLE=CATEGORIES_TABLE)
        constraint = "WHERE ch.id = {id}".format(id=check_id)
        return self.__select_query(columns, tables, constraint)

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
        return self.__select_query("id", CATEGORIES_TABLE)[0][0]

    def categories(self):
        return self.__select_all_query(CATEGORIES_TABLE)

    def add_category(self, name):
        self.__insert_query(CATEGORIES_TABLE, "(name)", "('{}')".format(name))
        return self.category_id(name)

    #
    # Queries
    #

    def __connect(self, user, password, host, port, db_name):
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

    def __query_with_args(self, command, tableName, constraint=""):
        query = command + " " + tableName + " " + constraint
        return self.query(query)

    def __update_query(self, tableName, set, constraint=""):
        self.__query_with_args("UPDATE", tableName, " SET " + set + " " + constraint)

    def __insert_query(self, tableName, where, what):
        self.__query_with_args("INSERT INTO", tableName, where + " VALUES " + what)

    def __select_query(self, columns, tableName, constraint=""):
        return self.__query_with_args("SELECT {columns} FROM ".format(columns=columns), tableName, constraint)

    def __select_top_query(self, n, tableName, columns="*", constraint=""):
        return self.__select_query(columns, tableName, constraint + "LIMIT {}".format(n))

    def __select_all_query(self, tableName, constraint=""):
        return self.__select_query("*", tableName, constraint)


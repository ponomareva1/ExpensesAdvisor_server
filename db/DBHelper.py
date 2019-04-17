import logging
import os

import psycopg2 as pg
from db.DBConstants import *

logger = logging.getLogger(__name__)


class DBHelper:

    def __init__(self, remote=True, connect_params=None):
        try:
            if remote:
                database_url = os.environ['DATABASE_URL']
                self.connection = pg.connect(database_url, sslmode='require')
            else:
                self.connection = pg.connect(**connect_params)
        except Exception as e:
            logger.error("CONNECTION ERROR:")
            logger.error(e)

    def __del__(self):
        self.connection.close()

    #
    # User API
    #
    def users(self):
        users = self.__select_all_query(USERS_TABLE)
        if users is not None:
            fields = ['id', 'username', 'password']
            return [dict(zip(fields, user)) for user in users]

    def add_user(self, login: str, password: str):
        values = "('{login}','{password}')".format(login=login, password=password)
        self.__insert_query(USERS_TABLE, "(login,password)", values)
        return self.user_id(login)

    def user_login(self, user_id: int):
        user_login = self.__select_query("login", USERS_TABLE, "WHERE id = '{}'".format(user_id))
        if user_login is not None:
            return user_login[0][0]

    def user_password(self, login: str):
        user_password = self.__select_query("password", USERS_TABLE, "WHERE login = '{}'".format(login))
        if user_password is not None:
            return user_password[0][0]

    def user_id(self, login: str):
        user_id = self.__select_query("id", USERS_TABLE, "WHERE login = '{}'".format(login))
        if user_id is not None:
            return user_id[0][0]

    def user_exist(self, login: str):
        return self.__check_if_exist(USERS_TABLE, "login", login)

    #
    # Checks API
    #
    def add_check(self, specifier: str, shop: str, date, login: str):
        user_id = self.user_id(login)
        self.__insert_query(CHECKS_TABLE,
                            "(specifier,shop,date,id_user)",
                            "('{specifier}','{shop}','{date}',{user_id})".format(specifier=specifier, shop=shop,
                                                                                 date=date, user_id=user_id))
        return self.check_id(specifier)

    def get_last_checks(self, limit: int, login: str):
        user_id = self.user_id(login)
        columns = "ch.id, ch.shop, ch.date, sum(i.price)"
        tables = "{CHECKS_TABLE} ch JOIN {ITEMS_TABLE} i ON ch.id = i.id_check".format(ITEMS_TABLE=ITEMS_TABLE,
                                                                                       CHECKS_TABLE=CHECKS_TABLE)
        constraint = """WHERE ch.id_user = {user_id}
                        GROUP BY ch.id
                        ORDER BY ch.date DESC
                        LIMIT {limit}
                        """.format(user_id=user_id, limit=limit)
        checks = self.__select_query(columns, tables, constraint)
        if checks is not None:
            fields = ['id', 'shop', 'date', 'sum']
            return [dict(zip(fields, check)) for check in checks]

    def check_id(self, specifier: str):
        check_id = self.__select_query("id", CHECKS_TABLE, "WHERE specifier = '{}'".format(specifier))
        if check_id is not None:
            return check_id[0][0]

    def check_exist(self, check_id: int):
        return self.__check_if_exist(CHECKS_TABLE, "id", check_id)

    def check_unique(self, specifier: str):
        return not self.__check_if_exist(CHECKS_TABLE, "specifier", specifier)

    #
    # Items API
    #
    def items_info(self, check_id: int):
        columns = "i.id,i.name,price,quant,c.name AS category"
        tables = """{ITEMS_TABLE} i JOIN {CHECKS_TABLE} ch ON ch.id = i.id_check 
                                    JOIN {CATEGORIES_TABLE} c ON c.id = i.id_category""". \
            format(ITEMS_TABLE=ITEMS_TABLE,
                   CHECKS_TABLE=CHECKS_TABLE,
                   CATEGORIES_TABLE=CATEGORIES_TABLE)
        constraint = "WHERE ch.id = {id}".format(id=check_id)
        items = self.__select_query(columns, tables, constraint)
        if items is not None:
            fields = ['id', 'name', 'price', 'quantity', 'category']
            return [dict(zip(fields, item)) for item in items]

    def add_item(self, name: str, price: float, quant: int, check_id: int, category_id: int):
        self.__insert_query(ITEMS_TABLE, "(name,price,quant,id_category,id_check)",
                            "('{name}',{price},{quant},{category_id},{check_id})".format(name=name, price=price,
                                                                                         quant=quant, check_id=check_id,
                                                                                         category_id=category_id))
        return self.item_id(name, check_id)

    def item_id(self, name: str, check_id: int):
        item_id = self.__select_query("id", ITEMS_TABLE, "WHERE name = '{name}' "
                                                         "AND id_check = {check_id}".format(name=name,
                                                                                            check_id=check_id))
        if item_id is not None:
            return item_id[0][0]

    def item_exist(self, item_id: int):
        return self.__check_if_exist(ITEMS_TABLE, "id", item_id)

    #
    # Category API
    #
    def update_category(self, item_id: int, new_category_id: int):
        constraint = """WHERE id = {item_id}""".format(item_id=item_id)
        self.__update_query(ITEMS_TABLE, "id_category = {} ".format(new_category_id), constraint)

    def category_id(self, name: str):
        category_id = self.__select_query("id", CATEGORIES_TABLE, "WHERE name = '{name}'".format(name=name))
        if category_id is not None:
            return category_id[0][0]

    def categories(self):
        categories = self.__select_all_query(CATEGORIES_TABLE)
        if not categories:
            return None

        categories_list = list()
        for category in categories:
            categories_list.append(category[1])

        return categories_list

    def add_category(self, name: str):
        self.__insert_query(CATEGORIES_TABLE, "(name)", "('{}')".format(name))
        return self.category_id(name)

    def category_exist(self, name: str):
        return self.__check_if_exist(CATEGORIES_TABLE, "name", name)

    #
    # WaitingCodes API
    #
    def waiting_codes(self):
        waiting_codes = self.__select_all_query(WAITING_CODES_TABLE)
        if waiting_codes is not None:
            fields = ['user_id', 'json', 'id']
            return [dict(zip(fields, waiting_code)) for waiting_code in waiting_codes]

    def add_waiting_code(self, login: str, json: str):
        user_id = self.user_id(login)
        self.__insert_query(WAITING_CODES_TABLE,
                            "(json,user_id)",
                            "('{json}',{user_id})".format(json=json, user_id=user_id))

    def delete_waiting_code(self, id: int):
        self.__delete_query(WAITING_CODES_TABLE, "id = {}".format(id))

    #
    # Statistics API
    #
    def statistics_categories(self, login: str):
        user_id = self.user_id(login)
        columns = "c.name category, sum(i.price) as sum"
        tables = """{ITEMS_TABLE} i JOIN {CHECKS_TABLE} ch ON ch.id = i.id_check 
                        JOIN {CATEGORIES_TABLE} c ON c.id = i.id_category""". \
            format(ITEMS_TABLE=ITEMS_TABLE,
                   CHECKS_TABLE=CHECKS_TABLE,
                   CATEGORIES_TABLE=CATEGORIES_TABLE)

        constraint = """WHERE ch.id_user = {id} 
                        GROUP BY c.name""".format(id=user_id)
        statistics = self.__select_query(columns, tables, constraint)
        if statistics is not None:
            fields = ['category', 'sum']
            return [dict(zip(fields, statistic)) for statistic in statistics]

    def statistics_daily(self, login: str):
        user_id = self.user_id(login)
        query = """
                WITH
                  days AS (
                      SELECT generate_series(current_date-10, current_date+1, '1d')::date AS day
                  ),
                  checks AS (
                      SELECT * FROM public."Checks" ch WHERE ch.id_user = {user_id}
                  )
                SELECT days.day as day, CASE WHEN sum(i.price) is NULL THEN 0 ELSE sum(i.price) END AS sum
                FROM days LEFT JOIN checks ch on days.day = ch.date::date
                  LEFT JOIN public."Items" i on ch.id = i.id_check 
                GROUP BY days.day ORDER BY days.day
        """.format(user_id=user_id)
        statistics = self.query(query)
        if statistics is not None:
            fields = ['day', 'sum']
            return [dict(zip(fields, statistic)) for statistic in statistics]

    #
    # Queries
    #
    def query(self, query: str):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            rows = None
            if cursor.rowcount > 0 and cursor.description is not None:
                rows = cursor.fetchall()
            self.connection.commit()
            return rows
        except Exception as e:
            self.connection.rollback()
            logger.warning("Error with query : {}".format(query))
            logger.warning(e)
        finally:
            cursor.close()

    def __query_with_args(self, command: str, table_name: str, constraint=""):
        query = command + " " + table_name + " " + constraint
        return self.query(query)

    def __update_query(self, table_name: str, what: str, constraint=""):
        self.__query_with_args("UPDATE", table_name, " SET " + what + " " + constraint)

    def __insert_query(self, table_name: str, where: str, what: str):
        self.__query_with_args("INSERT INTO", table_name, where + " VALUES " + what)

    def __delete_query(self, table_name: str, where: str):
        self.__query_with_args("DELETE FROM", table_name, "WHERE {}".format(where))

    def __select_query(self, columns: str, table_name: str, constraint=""):
        return self.__query_with_args("SELECT {columns} FROM ".format(columns=columns), table_name, constraint)

    def __select_all_query(self, table_name: str, constraint=""):
        return self.__select_query("*", table_name, constraint)

    def __check_if_exist(self, table_name: str, field: str, field_data):
        query = """SELECT CASE WHEN EXISTS (
                                            SELECT *
                                            FROM {table_name}
                                            WHERE {field} = '{field_data}'
                                )
                                THEN True
                                ELSE False END""".format(table_name=table_name, field=field, field_data=field_data)
        return self.query(query)[0][0]

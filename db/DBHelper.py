import postgresql as pg
from os import listdir
from db.date.ItemInfo import ItemInfo

CHECKS_TABLE = "\"Checks\""
USERS_TABLE = "\"Users\""
ITEMS_TABLE = "\"Items\""
CATEGORIES_TABLE = "\"Categories\""
PATTERNS_TABLE = "\"Patterns\""

USER = "postgres"
PASS = ""
HOST = "localhost"
PORT = "5432"
DB_NAME = "QrCodesDB"

DB_PARAMS = 'pq://' + USER + ':' + PASS + '@' + HOST + ':' + PORT + '/' + DB_NAME

SCRIPTS_PATH = "scripts/"
SEQ_SCRIPTS_PATH = SCRIPTS_PATH + "seq/"
TAB_SCRIPTS_PATH = SCRIPTS_PATH + "tables/"


# TODO: methods for statistic
# TODO: methods for waiting chacks


class DBHelper:

    def __init__(self, local=True, user="", password="", host="", port="", db_name=""):
        try:
            if local:
                try:
                    self.__create_new_db()
                    self.db = self.__conect_to_local()
                except pg.exceptions.ClientCannotConnectError:
                    print("<INFO>: Attempt to create a new database:\n" + DB_PARAMS)
                    self.db = self.__create_new_db()
            else:
                self.db = self.__connect(user, password, host, port, db_name)
        except pg.exceptions.ClientCannotConnectError:
            print("CONNECTION ERROR")

    #
    # User API
    #
    def users(self):
        return self.__selectAllQuery(USERS_TABLE)

    def addUser(self, login, password):
        # TODO: login&pass checking
        values = "('" + login + "','" + password + "')"
        self.__insertQuery(USERS_TABLE, "(login,password)", values)

    def userExist(self, login):
        query = """SELECT CASE WHEN EXISTS (
                                    SELECT *
                                    FROM %s
                                    WHERE login = '%s'
                    )
                    THEN True
                    ELSE False END""" % (USERS_TABLE, login)
        return self.db.query(query)[0][0]

    def userId(self, login):
        return self.__selectQuery("id", USERS_TABLE, "WHERE login = '%s'" % login)[0][0]

    #
    # Checks API
    #
    def checks(self):
        return self.__selectAllQuery(CHECKS_TABLE)

    def addCheck(self, specifier, shop, date, login):
        # TODO: specifier must be unique
        userId = self.userId(login)
        self.__insertQuery(CHECKS_TABLE,
                           "(specifier,shop,date,id_user)",
                           "('%s','%s','%s',%d)" % (specifier, shop, date, userId)
                           )

    def getLastChecks(self, n, login):
        if (not self.userExist(login)):
            raise Exception("User with login '%s' doesn't exist" % login)
        userId = self.userId(login)
        return self.__selectTopQuery(n, CHECKS_TABLE, constraint="WHERE id_user = %d" % userId)

    #
    # Items API
    #
    def itemsInfo(self, checkId):
        columns = "i.name,price,quant,c.name AS category"
        tables = """%s i 
                    JOIN %s ch ON ch.id = i.id_check 
                    JOIN %s c ON c.id = i.id_category""" % (ITEMS_TABLE, CHECKS_TABLE, CATEGORIES_TABLE)
        constraint = "WHERE ch.id = %d" % checkId
        return ItemInfo(self.__selectQuery(columns, tables, constraint)[0])

    #
    # Category API
    #
    def updateCategorie(self, checkId, itemId, new_category):
        # TODO + QUATION: update all such items or only item in this check ???
        # UPDATE "Items" SET id_category = 6;
        id = self.categoryId(new_category)
        constraint = """WHERE id_check = %d AND id = %d""" % (checkId, itemId)
        self.__query("UPDATE", ITEMS_TABLE, "SET id_category = " + id)

    def categoryId(self, name):
        return self.__selectQuery("(id)", CATEGORIES_TABLE)[0][0]

    def categories(self):
        return self.__selectAllQuery(CATEGORIES_TABLE)

    def addCategory(self, name):
        # TODO name category must be unique
        self.__insertQuery(CATEGORIES_TABLE, "(name)", "('%s')" % name)

    def __connect(self, user, password, host, port, db_name):
        return pg.open('pq://' + user + ':' + password + '@' + host + ':' + port + '/' + db_name)

    def __conect_to_local(self):
        return self.__connect(USER, PASS, HOST, PORT, DB_NAME)

    def __query(self, command, tableName, constraint=""):
        return self.db.query(command + " " + tableName + " " + constraint)

    def __insertQuery(self, tableName, where, what):
        self.__query("INSERT INTO", tableName, where + " VALUES " + what)

    def __selectQuery(self, columns, tableName, constraint=""):
        return self.__query("SELECT %s FROM " % columns, tableName, constraint)

    def __selectTopQuery(self, n, tableName, columns="*", constraint=""):
        return self.__selectQuery(columns, tableName, constraint + "LIMIT %d" % n)

    def __selectAllQuery(self, tableName, constraint=""):
        return self.__selectQuery("*", tableName, constraint)

    def __create_new_db(self):
        connection = pg.open('pq://' + USER + ':' + PASS + '@' + HOST + ':' + PORT)
        connection.execute("CREATE DATABASE " + DB_NAME)
        self.__create_in_db(connection, SEQ_SCRIPTS_PATH)
        self.__create_in_db(connection, TAB_SCRIPTS_PATH)

    def __create_in_db(self, connection, path):
        file_names = [path + f for f in listdir(path)]
        scripts = [open(f).read() for f in file_names]
        for script in scripts:
            connection.execute(script)

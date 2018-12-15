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
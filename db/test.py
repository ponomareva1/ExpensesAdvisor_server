from db.DBHelper import DBHelper
from datetime import datetime

db = DBHelper()


db.add_user("login", "password")
# category_id = db.add_category("fruit")
# check_id = db.add_check("dfghj", "shop", datetime.now().__str__(), "login")
# db.add_item("banana", 27, 2, check_id, category_id)

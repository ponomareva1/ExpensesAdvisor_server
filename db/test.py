from db.DBHelper import DBHelper
from datetime import datetime

db = DBHelper()

user_id = db.add_user("login", "password")
category_id = db.add_category("fruit")
check_id = db.add_check("dfghj", "shop", datetime.now().__str__(), user_id)
item_id = db.add_item("banana", 27, 2, check_id, category_id)
new_category_id = db.add_category('not fruit')
print(db.items_info(1))
print(db.categories())
db.update_category(1, item_id, new_category_id)

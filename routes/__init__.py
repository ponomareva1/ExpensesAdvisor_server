from flask import Blueprint

qrcode_route = Blueprint('QRcode', __name__)
checks_route = Blueprint('checks', __name__)
items_route = Blueprint('items', __name__)
user_route = Blueprint('user', __name__)
statistics_route = Blueprint('statistics', __name__)

from .qr_code import *
from .checks import *
from .items import *
from .user import *
from .statistics import *

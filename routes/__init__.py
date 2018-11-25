from flask import Blueprint
qrcode_route = Blueprint('QRcode', __name__)
checks_route = Blueprint('checks', __name__)
items_route = Blueprint('items', __name__)

from .qr_code import *
from .checks import *
from .items import *

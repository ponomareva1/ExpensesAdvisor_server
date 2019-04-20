import logging

import requests

from schemas.schemas import QRcode

logger = logging.getLogger("fns_connector")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("fnsConnection.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class FNSConnector:
    def __init__(self):
        self.base_url = "https://proverkacheka.nalog.ru:9999/v1/"
        self.paths = {
            'login': "mobile/users/login",
            'check': "ofds/*/inns/*/fss/{fn}/operations/1/tickets/{fd}?fiscalSign={fp}&date={t}&sum={s}",
            'info': "inns/*/kkts/*/fss/{fn}/tickets/{fd}?fiscalSign={fp}&sendToEmail=no"
        }

        self.username = "+79112334772"
        self.password = "536702"

    def login(self):
        url = self.base_url + self.paths['login']

        try:
            response = requests.get(url, auth=(self.username, self.password))
        except requests.exceptions.Timeout:
            logger.error("Gateway Timeout while FNS login")
            raise ConnectionError("Not able to login in FNS")

        if not response.ok:
            logger.error("Not able to login in FNS: {username}, {password}".format(username=self.username,
                                                                                   password=self.password))
            raise ConnectionError("Not able to login in FNS")

        logger.info("Successful login")

    def is_qrcode_correct(self, qrcode: QRcode):
        prepared_url = self.base_url + self.paths['check']
        url = self.format_url(prepared_url, qrcode)

        try:
            response = requests.get(url)
        except requests.exceptions.Timeout:
            logger.error("Gateway Timeout while request to {}".format(prepared_url))
            raise ConnectionError

        if response.ok:
            logger.info("Correct QR code info / Check found")
            logger.info("QR code: {}".format(vars(qrcode)))
            return True
        else:
            logger.error("Incorrect QR code info / Check not found")
            logger.error("QR code: {}".format(vars(qrcode)))
            return False

    def get_check(self, qrcode: QRcode):
        prepared_url = self.base_url + self.paths['info']
        url = self.format_url(prepared_url, qrcode)

        try:
            response = requests.get(url,
                                    headers={"device-Id": "", "device-os": ""},
                                    auth=(self.username, self.password))
        except requests.exceptions.Timeout:
            logger.error("Gateway Timeout while request to {}".format(prepared_url))
            raise ConnectionError

        if response.ok:
            logger.info("Check received from server")

            if response.text == '':
                logger.warning("Empty check body")
                return None
            check = response.json()['document']['receipt']
            logger.info("Check: {}".format(check))
            return check
        else:
            logger.error("Was not able to receive check from server")
            logger.error("QR code: {}".format(vars(qrcode)))
            return None

    @staticmethod
    def format_url(prepared_url, qrcode: QRcode):
        return prepared_url.format(t=qrcode.t,
                                   fn=qrcode.fn,
                                   fp=qrcode.fp,
                                   fd=qrcode.fd,
                                   s=qrcode.s)


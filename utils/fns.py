import logging

import requests

from shemas.shemas import QRcode

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
            response = requests.get(url, auth=(self.username, self.password), timeout=0.1)
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
            response = requests.get(url, timeout=0.1)
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
                                    auth=(self.username, self.password),
                                    timeout=0.1)
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


if __name__ == '__main__':
    fns_connector = FNSConnector()
    fns_connector.login()

    qrcode1 = QRcode(t="20180927T1801",
                     fn="9282000100155754",
                     fp="2472140768",
                     fd="8723",
                     s="32877")

    qrcode2 = QRcode(t="20181122T2119",
                     fn="9282000100043216",
                     fp="3013868136",
                     fd="166128",
                     s="139501")

    qrcode3 = QRcode(t="20181108T1433",
                     fn="8710000101497815",
                     fp="2592181763",
                     fd="50071",
                     s="151200")

    if fns_connector.is_qrcode_correct(qrcode1):
        print(fns_connector.get_check(qrcode1))

    if fns_connector.is_qrcode_correct(qrcode2):
        print(fns_connector.get_check(qrcode2))

    if fns_connector.is_qrcode_correct(qrcode3):
        print(fns_connector.get_check(qrcode3))

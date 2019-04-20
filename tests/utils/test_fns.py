import unittest
import json
from utils.fns import FNSConnector
from schemas.schemas import QRcode

expected_check = '''{"operator": "Хоботова Ольга", "rawData": "pQMBEJmSggABABVXVAAiE0/5ZAgtACGmAAIChgMAggIRBBAAOTI4MjAwMDEwMDE1NTc1NA0EFAAwMDAxMTY1NzY5MDAxMzUyICAgIPoDDAA3ODI1NzA2MDg2ICAQBAQAEyIAAPQDBADcGq1bNQQGADEEk1nf4A4EBAAwAAAAEgQEAG0AAAAeBAEAAfwDAgBtgDwEDwA9BAMAiq6kPgQEADYwMjQjBEUABgQnADIxMzc2NTQgjoOOIIegouLgLoyekS6noK8u4ePlLu+hq66qMzUwozcEAgD+H/8DBAAGQEIPEwQCAP4fTwQCAOkCIwRFAAYEJwAyMTM3NjU0II6DjiCHoKLi4C6MnpEup6CvLuHj5S7voauuqjM1MKM3BAIA/h//AwQABkBCDxMEAgD+H08EAgDpAiMERgAGBCgAKjM2MDY1MzMgTUlMS0EgmK6qLkJVQkJMRVMgqq6qruEuraDnLjk3ozcEAgCHE/8DBAAGQEIPEwQCAIcTTgQCAPsCIwRFAAYEJwAzNDI2NzAwIE9SLpClp6itLkJVQi6BhYuOkY2Fhi6mpaIuMTMsNqM3BAIAwwn/AwQABkBCDxMEAgDDCU4EAgB9ASMERAAGBCYAKjMyMjg2MjUgUFJJTi6XqK/hLqqg4OIu4SDhrKXiL6vjqjE2NaM3BAIAJyP/AwQABkBCDxMEAgAnI04EAgBdBf0DDgCVrqGu4q6ioCCOq+yjoAcEAQAAOQQCAG2ATgQCANUJTwQCANIFGAQMAICj4K7iruCjII6OjvEDTwAxOTIwMTIsIJGgrariLY+l4qXgoePgoyCjLiwgjqHj5a6i4aquqSCOoa7grq3rIK/gLeIsIKQuMTE2LCA2MDI0LCA2ODYtj+/ipeCu56qgHwQBAAE=", "nds10": 1490, "cashTotalSum": 0, "dateTime": "2018-09-27T18:01:00", "retailPlaceAddress": "192012, Санкт-Петербург г., Обуховской Обороны пр-т, д.116, 6024, 686-Пятерочка", "ecashTotalSum": 32877, "userInn": "7825706086", "user": "Агроторг ООО", "shiftNumber": 48, "requestNumber": 109, "totalSum": 32877, "kktRegId": "0001165769001352", "fiscalSign": 2472140768, "fiscalDriveNumber": "9282000100155754", "operationType": 1, "items": [{"price": 8190, "name": "2137654 ОГО Завтр.МЮС.зап.сух.яблок350г", "nds10": 745, "quantity": 1, "sum": 8190}, {"price": 8190, "name": "2137654 ОГО Завтр.МЮС.зап.сух.яблок350г", "nds10": 745, "quantity": 1, "sum": 8190}, {"price": 4999, "name": "*3606533 MILKA Шок.BUBBLES кокос.нач.97г", "nds18": 763, "quantity": 1, "sum": 4999}, {"price": 2499, "name": "3426700 OR.Резин.BUB.БЕЛОСНЕЖ.жев.13,6г", "nds18": 381, "quantity": 1, "sum": 2499}, {"price": 8999, "name": "*3228625 PRIN.Чипс.карт.с смет/лук165г", "nds18": 1373, "quantity": 1, "sum": 8999}], "nds18": 2517, "receiptCode": 3, "properties": [{"value": "6024", "key": "Код"}], "taxationType": 1, "fiscalDocumentNumber": 8723}'''


class FnsTest(unittest.TestCase):

    def setUp(self):
        self.fns = FNSConnector()

    def test_login(self):
        self.fns.login()

    def test_is_qrcode_correct(self):
        qrcode = QRcode(t="20180927T1801",
                        fn="9282000100155754",
                        fp="2472140768",
                        fd="8723",
                        s="32877")
        assert self.fns.is_qrcode_correct(qrcode)

    def test_is_qrcode_incorrect(self):
        qrcode = QRcode(t="20180927T1801",
                        fn="9282000100155754",
                        fp="2472140768",
                        fd="87123",
                        s="32877")
        assert self.fns.is_qrcode_correct(qrcode) == False

    def test_get_check(self):
        qrcode = QRcode(t="20180927T1801",
                        fn="9282000100155754",
                        fp="2472140768",
                        fd="8723",
                        s="32877")
        assert self.fns.get_check(qrcode) == json.loads(expected_check)

    def test_format_url(self):
        prepared_url = "https://proverkacheka.nalog.ru:9999/v1/ofds/*/inns/*/fss/{fn}/operations/1/tickets/{fd}?fiscalSign={fp}&date={t}&sum={s}"
        qrcode = QRcode(t="20180927T1801",
                        fn="9282000100155754",
                        fp="2472140768",
                        fd="8723",
                        s="32877")
        assert self.fns.format_url(prepared_url, qrcode)

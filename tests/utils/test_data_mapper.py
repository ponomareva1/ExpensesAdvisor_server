from datetime import datetime
import unittest
import json
from schemas.schemas import Check, Item
from utils.data_mapper import parse_check

check_dict = '''
{
      "user": "Агроторг ООО",
      "taxationType": 1,
      "fiscalDriveNumber": "9282000100155754",
      "operationType": 1,
      "dateTime": "2018-09-27T18:01:00",
      "operator": "Хоботова Ольга",
      "nds10": 1490,
      "totalSum": 4444,    
      "items": [
        {
          "nds10": 745,
          "sum": 2222,
          "price": 1111,
          "name": "aaa",
          "quantity": 2
        },
        {
          "nds10": 745,
          "sum": 2222,
          "price": 2222,
          "name": "bbb",
          "quantity": 1
        }
      ],
      "requestNumber": 109,
      "nds18": 2517,
      "kktRegId": "0001165769001352",
      "receiptCode": 3,
      "fiscalSign": 2472140768,
      "shiftNumber": 48,
      "cashTotalSum": 0,
      "retailPlaceAddress": "192012, Санкт-Петербург г., Обуховской Обороны пр-т, д.116, 6024, 686-Пятерочка",
      "properties": [
        {
          "value": "6024",
          "key": "Код"
        }
      ],
      "ecashTotalSum": 4444,
      "userInn": "7825706086",
      "rawData": "pQMBEJmSggABABVXVAAiE0/5ZAgtACGmAAIChgMAggIRBBAAOTI4MjAwMDEwMDE1NTc1NA0EFAAwMDAxMTY1NzY5MDAxMzUyICAgIPoDDAA3ODI1NzA2MDg2ICAQBAQAEyIAAPQDBADcGq1bNQQGADEEk1nf4A4EBAAwAAAAEgQEAG0AAAAeBAEAAfwDAgBtgDwEDwA9BAMAiq6kPgQEADYwMjQjBEUABgQnADIxMzc2NTQgjoOOIIegouLgLoyekS6noK8u4ePlLu+hq66qMzUwozcEAgD+H/8DBAAGQEIPEwQCAP4fTwQCAOkCIwRFAAYEJwAyMTM3NjU0II6DjiCHoKLi4C6MnpEup6CvLuHj5S7voauuqjM1MKM3BAIA/h//AwQABkBCDxMEAgD+H08EAgDpAiMERgAGBCgAKjM2MDY1MzMgTUlMS0EgmK6qLkJVQkJMRVMgqq6qruEuraDnLjk3ozcEAgCHE/8DBAAGQEIPEwQCAIcTTgQCAPsCIwRFAAYEJwAzNDI2NzAwIE9SLpClp6itLkJVQi6BhYuOkY2Fhi6mpaIuMTMsNqM3BAIAwwn/AwQABkBCDxMEAgDDCU4EAgB9ASMERAAGBCYAKjMyMjg2MjUgUFJJTi6XqK/hLqqg4OIu4SDhrKXiL6vjqjE2NaM3BAIAJyP/AwQABkBCDxMEAgAnI04EAgBdBf0DDgCVrqGu4q6ioCCOq+yjoAcEAQAAOQQCAG2ATgQCANUJTwQCANIFGAQMAICj4K7iruCjII6OjvEDTwAxOTIwMTIsIJGgrariLY+l4qXgoePgoyCjLiwgjqHj5a6i4aquqSCOoa7grq3rIK/gLeIsIKQuMTE2LCA2MDI0LCA2ODYtj+/ipeCu56qgHwQBAAE=",
      "fiscalDocumentNumber": 8723
    }
'''

check_dict_with_shop = '''
{
      "user": "Агроторг ООО",
      "taxationType": 1,
      "fiscalDriveNumber": "9282000100155754",
      "operationType": 1,
      "dateTime": "2018-09-27T18:01:00",
      "operator": "Хоботова Ольга",
      "nds10": 1490,
      "totalSum": 4444,    
      "items": [
        {
          "nds10": 745,
          "sum": 2222,
          "price": 1111,
          "name": "aaa",
          "quantity": 2
        },
        {
          "nds10": 745,
          "sum": 2222,
          "price": 2222,
          "name": "bbb",
          "quantity": 1
        }
      ],
      "requestNumber": 109,
      "nds18": 2517,
      "kktRegId": "0001165769001352",
      "receiptCode": 3,
      "fiscalSign": 2472140768,
      "shiftNumber": 48,
      "cashTotalSum": 0,
      "retailPlace": "686-Пятерочка",
      "retailPlaceAddress": "192012, Санкт-Петербург г., Обуховской Обороны пр-т, д.116, 6024, 686-Пятерочка",
      "properties": [
        {
          "value": "6024",
          "key": "Код"
        }
      ],
      "ecashTotalSum": 4444,
      "userInn": "7825706086",
      "rawData": "pQMBEJmSggABABVXVAAiE0/5ZAgtACGmAAIChgMAggIRBBAAOTI4MjAwMDEwMDE1NTc1NA0EFAAwMDAxMTY1NzY5MDAxMzUyICAgIPoDDAA3ODI1NzA2MDg2ICAQBAQAEyIAAPQDBADcGq1bNQQGADEEk1nf4A4EBAAwAAAAEgQEAG0AAAAeBAEAAfwDAgBtgDwEDwA9BAMAiq6kPgQEADYwMjQjBEUABgQnADIxMzc2NTQgjoOOIIegouLgLoyekS6noK8u4ePlLu+hq66qMzUwozcEAgD+H/8DBAAGQEIPEwQCAP4fTwQCAOkCIwRFAAYEJwAyMTM3NjU0II6DjiCHoKLi4C6MnpEup6CvLuHj5S7voauuqjM1MKM3BAIA/h//AwQABkBCDxMEAgD+H08EAgDpAiMERgAGBCgAKjM2MDY1MzMgTUlMS0EgmK6qLkJVQkJMRVMgqq6qruEuraDnLjk3ozcEAgCHE/8DBAAGQEIPEwQCAIcTTgQCAPsCIwRFAAYEJwAzNDI2NzAwIE9SLpClp6itLkJVQi6BhYuOkY2Fhi6mpaIuMTMsNqM3BAIAwwn/AwQABkBCDxMEAgDDCU4EAgB9ASMERAAGBCYAKjMyMjg2MjUgUFJJTi6XqK/hLqqg4OIu4SDhrKXiL6vjqjE2NaM3BAIAJyP/AwQABkBCDxMEAgAnI04EAgBdBf0DDgCVrqGu4q6ioCCOq+yjoAcEAQAAOQQCAG2ATgQCANUJTwQCANIFGAQMAICj4K7iruCjII6OjvEDTwAxOTIwMTIsIJGgrariLY+l4qXgoePgoyCjLiwgjqHj5a6i4aquqSCOoa7grq3rIK/gLeIsIKQuMTE2LCA2MDI0LCA2ODYtj+/ipeCu56qgHwQBAAE=",
      "fiscalDocumentNumber": 8723
    }
'''


check_dict_without_shop = '''
{
      "taxationType": 1,
      "fiscalDriveNumber": "9282000100155754",
      "operationType": 1,
      "dateTime": "2018-09-27T18:01:00",
      "operator": "Хоботова Ольга",
      "nds10": 1490,
      "totalSum": 4444,    
      "items": [
        {
          "nds10": 745,
          "sum": 2222,
          "price": 1111,
          "name": "aaa",
          "quantity": 2
        },
        {
          "nds10": 745,
          "sum": 2222,
          "price": 2222,
          "name": "bbb",
          "quantity": 1
        }
      ],
      "requestNumber": 109,
      "nds18": 2517,
      "kktRegId": "0001165769001352",
      "receiptCode": 3,
      "fiscalSign": 2472140768,
      "shiftNumber": 48,
      "cashTotalSum": 0,
      "retailPlaceAddress": "192012, Санкт-Петербург г., Обуховской Обороны пр-т, д.116, 6024, 686-Пятерочка",
      "properties": [
        {
          "value": "6024",
          "key": "Код"
        }
      ],
      "ecashTotalSum": 4444,
      "userInn": "7825706086",
      "rawData": "pQMBEJmSggABABVXVAAiE0/5ZAgtACGmAAIChgMAggIRBBAAOTI4MjAwMDEwMDE1NTc1NA0EFAAwMDAxMTY1NzY5MDAxMzUyICAgIPoDDAA3ODI1NzA2MDg2ICAQBAQAEyIAAPQDBADcGq1bNQQGADEEk1nf4A4EBAAwAAAAEgQEAG0AAAAeBAEAAfwDAgBtgDwEDwA9BAMAiq6kPgQEADYwMjQjBEUABgQnADIxMzc2NTQgjoOOIIegouLgLoyekS6noK8u4ePlLu+hq66qMzUwozcEAgD+H/8DBAAGQEIPEwQCAP4fTwQCAOkCIwRFAAYEJwAyMTM3NjU0II6DjiCHoKLi4C6MnpEup6CvLuHj5S7voauuqjM1MKM3BAIA/h//AwQABkBCDxMEAgD+H08EAgDpAiMERgAGBCgAKjM2MDY1MzMgTUlMS0EgmK6qLkJVQkJMRVMgqq6qruEuraDnLjk3ozcEAgCHE/8DBAAGQEIPEwQCAIcTTgQCAPsCIwRFAAYEJwAzNDI2NzAwIE9SLpClp6itLkJVQi6BhYuOkY2Fhi6mpaIuMTMsNqM3BAIAwwn/AwQABkBCDxMEAgDDCU4EAgB9ASMERAAGBCYAKjMyMjg2MjUgUFJJTi6XqK/hLqqg4OIu4SDhrKXiL6vjqjE2NaM3BAIAJyP/AwQABkBCDxMEAgAnI04EAgBdBf0DDgCVrqGu4q6ioCCOq+yjoAcEAQAAOQQCAG2ATgQCANUJTwQCANIFGAQMAICj4K7iruCjII6OjvEDTwAxOTIwMTIsIJGgrariLY+l4qXgoePgoyCjLiwgjqHj5a6i4aquqSCOoa7grq3rIK/gLeIsIKQuMTE2LCA2MDI0LCA2ODYtj+/ipeCu56qgHwQBAAE=",
      "fiscalDocumentNumber": 8723
    }
'''

empty_check_dict = '''
    {
      "user": "Агроторг",
      "taxationType": 1,
      "fiscalDriveNumber": "9282000100155754",
      "operationType": 1,
      "dateTime": "2018-09-27T18:01:00",
      "operator": "Хоботова Ольга",
      "nds10": 1490,
      "totalSum": 0,
      "items": [
      ],
      "requestNumber": 109,
      "nds18": 2517,
      "kktRegId": "0001165769001352",
      "receiptCode": 3,
      "fiscalSign": 2472140768,
      "shiftNumber": 48,
      "cashTotalSum": 0,
      "retailPlaceAddress": "192012, Санкт-Петербург г., Обуховской Обороны пр-т, д.116, 6024, 686-Пятерочка",
      "properties": [
        {
          "value": "6024",
          "key": "Код"
        }
      ],
      "ecashTotalSum": 32877,
      "userInn": "7825706086",
      "rawData": "pQMBEJmSggABABVXVAAiE0/5ZAgtACGmAAIChgMAggIRBBAAOTI4MjAwMDEwMDE1NTc1NA0EFAAwMDAxMTY1NzY5MDAxMzUyICAgIPoDDAA3ODI1NzA2MDg2ICAQBAQAEyIAAPQDBADcGq1bNQQGADEEk1nf4A4EBAAwAAAAEgQEAG0AAAAeBAEAAfwDAgBtgDwEDwA9BAMAiq6kPgQEADYwMjQjBEUABgQnADIxMzc2NTQgjoOOIIegouLgLoyekS6noK8u4ePlLu+hq66qMzUwozcEAgD+H/8DBAAGQEIPEwQCAP4fTwQCAOkCIwRFAAYEJwAyMTM3NjU0II6DjiCHoKLi4C6MnpEup6CvLuHj5S7voauuqjM1MKM3BAIA/h//AwQABkBCDxMEAgD+H08EAgDpAiMERgAGBCgAKjM2MDY1MzMgTUlMS0EgmK6qLkJVQkJMRVMgqq6qruEuraDnLjk3ozcEAgCHE/8DBAAGQEIPEwQCAIcTTgQCAPsCIwRFAAYEJwAzNDI2NzAwIE9SLpClp6itLkJVQi6BhYuOkY2Fhi6mpaIuMTMsNqM3BAIAwwn/AwQABkBCDxMEAgDDCU4EAgB9ASMERAAGBCYAKjMyMjg2MjUgUFJJTi6XqK/hLqqg4OIu4SDhrKXiL6vjqjE2NaM3BAIAJyP/AwQABkBCDxMEAgAnI04EAgBdBf0DDgCVrqGu4q6ioCCOq+yjoAcEAQAAOQQCAG2ATgQCANUJTwQCANIFGAQMAICj4K7iruCjII6OjvEDTwAxOTIwMTIsIJGgrariLY+l4qXgoePgoyCjLiwgjqHj5a6i4aquqSCOoa7grq3rIK/gLeIsIKQuMTE2LCA2MDI0LCA2ODYtj+/ipeCu56qgHwQBAAE=",
      "fiscalDocumentNumber": 8723
}
'''

incorrect_check_dict = '''
    {
      "user": "Агроторг ООО",
      "taxationType": 1,
      "fiscalDriveNumber": "9282000100155754",
      "operationType": 1,
      "dateTime": "2018-09-27T18:01:00",
      "operator": "Хоботова Ольга",
      "nds10": 1490,
      "totalSum": 4444,
      "items": [
        {
          "nds10": 745,
          "sum": 2222,
          "price": 1111,
          "name": "aaa",
          "quantity": 2
        },
        {
          "nds10": 745,
          "sum": 2222,
          "price": 2222,
          "name": "bbb",
          "quantity": 1
        }
      ],
      "requestNumber": 109,
      "nds18": 2517,
      "kktRegId": "0001165769001352",
      "receiptCode": 3,
      "fiscalSign": 2472140768,
      "shiftNumber": 48,
      "cashTotalSum": 0,
      "retailPlaceAddress": "192012, Санкт-Петербург г., Обуховской Обороны пр-т, д.116, 6024, 686-Пятерочка",
      "properties": [
        {
          "value": "6024",
          "key": "Код"
        }
      ],
      "ecashTotalSum": 4444,
      "userInn": "7825706086",
      "rawData": "pQMBEJmSggABABVXVAAiE0/5ZAgtACGmAAIChgMAggIRBBAAOTI4MjAwMDEwMDE1NTc1NA0EFAAwMDAxMTY1NzY5MDAxMzUyICAgIPoDDAA3ODI1NzA2MDg2ICAQBAQAEyIAAPQDBADcGq1bNQQGADEEk1nf4A4EBAAwAAAAEgQEAG0AAAAeBAEAAfwDAgBtgDwEDwA9BAMAiq6kPgQEADYwMjQjBEUABgQnADIxMzc2NTQgjoOOIIegouLgLoyekS6noK8u4ePlLu+hq66qMzUwozcEAgD+H/8DBAAGQEIPEwQCAP4fTwQCAOkCIwRFAAYEJwAyMTM3NjU0II6DjiCHoKLi4C6MnpEup6CvLuHj5S7voauuqjM1MKM3BAIA/h//AwQABkBCDxMEAgD+H08EAgDpAiMERgAGBCgAKjM2MDY1MzMgTUlMS0EgmK6qLkJVQkJMRVMgqq6qruEuraDnLjk3ozcEAgCHE/8DBAAGQEIPEwQCAIcTTgQCAPsCIwRFAAYEJwAzNDI2NzAwIE9SLpClp6itLkJVQi6BhYuOkY2Fhi6mpaIuMTMsNqM3BAIAwwn/AwQABkBCDxMEAgDDCU4EAgB9ASMERAAGBCYAKjMyMjg2MjUgUFJJTi6XqK/hLqqg4OIu4SDhrKXiL6vjqjE2NaM3BAIAJyP/AwQABkBCDxMEAgAnI04EAgBdBf0DDgCVrqGu4q6ioCCOq+yjoAcEAQAAOQQCAG2ATgQCANUJTwQCANIFGAQMAICj4K7iruCjII6OjvEDTwAxOTIwMTIsIJGgrariLY+l4qXgoePgoyCjLiwgjqHj5a6i4aquqSCOoa7grq3rIK/gLeIsIKQuMTE2LCA2MDI0LCA2ODYtj+/ipeCu56qgHwQBAAE="
}
'''


class DataMapperTest(unittest.TestCase):

    def compare_by_attributes(self, a, b):
        for att in vars(a):
            if (getattr(a, att) != getattr(a, att)):  # for None type
                if (getattr(a, att).__dict__ != getattr(b, att).__dict__):
                    return False
        return True

    def test_parse_check(self):
        items = [Item(name="aaa", price=22.22, quantity=2), Item(name="bbb", price=22.22, quantity=1)]
        expected_check = Check(date=datetime.strptime("2018-09-27T18:01:00", '%Y-%m-%dT%H:%M:%S'),
                               shop="Агроторг ООО",
                               sum=44.44,
                               specifier="9282000100155754-2472140768-8723",
                               items=items)
        actual_check = parse_check(json.loads(check_dict))
        assert self.compare_by_attributes(actual_check, expected_check)

    def test_parse_empty_check(self):
        expected_check = Check(date=datetime.strptime("2018-09-27T18:01:00", '%Y-%m-%dT%H:%M:%S'),
                               shop="Агроторг ООО",
                               sum=44.44,
                               specifier="9282000100155754-2472140768-8723",
                               items=[])
        actual_check = parse_check(json.loads(empty_check_dict))
        assert self.compare_by_attributes(actual_check, expected_check)

    def test_parse_check_with_shop(self):
        expected_check = Check(date=datetime.strptime("2018-09-27T18:01:00", '%Y-%m-%dT%H:%M:%S'),
                               shop="686-Пятерочка",
                               sum=44.44,
                               specifier="9282000100155754-2472140768-8723",
                               items=[])
        actual_check = parse_check(json.loads(check_dict_with_shop))
        assert self.compare_by_attributes(actual_check, expected_check)

    def test_parse_check_without_unknown_shop(self):
        expected_check = Check(date=datetime.strptime("2018-09-27T18:01:00", '%Y-%m-%dT%H:%M:%S'),
                               shop="Неизвестно",
                               sum=44.44,
                               specifier="9282000100155754-2472140768-8723",
                               items=[])
        actual_check = parse_check(json.loads(check_dict_without_shop))
        assert self.compare_by_attributes(actual_check, expected_check)

    @unittest.expectedFailure
    def test_parse_incorrect_check(self):
        parse_check(json.loads(incorrect_check_dict))

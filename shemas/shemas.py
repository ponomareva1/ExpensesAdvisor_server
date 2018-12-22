class QRcode:
    def __init__(self, t, fn, fp, fd, s):
        self.t = t  # Дата + время
        self.fn = fn  # Номер ФН (Фискальный Номер)
        self.fp = fp  # Номер ФПД (Фискальный Признак Документа)
        self.fd = fd  # Номер ФД (Фискальный документ)
        self.s = s  # Сумма чека в копейках


class Category:
    def __init__(self, id, name):
        self.id = id  # ID категории
        self.name = name  # Категория


class Item:
    def __init__(self, name, price, quantity, id=None, category=None):
        self.id = id  # ID чека
        self.name = name  # Полное наименование товара
        self.price = price  # Цена
        self.quantity = quantity  # Количество / вес товара в кг
        self.category = category  # Наименование категории


class Check:
    def __init__(self, date, shop, sum, items, specifier, id=None):
        self.id = id  # ID чека
        self.date = date  # Дата совершения покупки
        self.shop = shop  # Магазин, в котором совершили покупку
        self.sum = sum  # Полная сумма
        self.items = items  # Список объектов Item
        self.specifier = specifier  # Специфичный идентификатор чека ({fn}-{fp}-{fd})


class MonthlyCategories:
    def __init__(self, category, sum):
        self.category = category  # Категория
        self.sum = sum  # Сумма по категории


class MeanCheck:
    def __init__(self, days, meanCheck):
        self.days = days  # Период, за который собрана статистика
        self.meanCheck = meanCheck  # Средний чек

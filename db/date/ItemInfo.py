class ItemInfo:
    def __init__(self, record):
        self.name = record['name']
        self.price = record['price']
        self.quant = record['quant']
        self.category = record['category']

    def __str__(self) -> str:
        str = "{\n"
        str += ("\tname : %s,\n" % self.name)
        str += ("\tprice : %s,\n" % self.price)
        str += ("\tquant : %s,\n" % self.quant)
        str += ("\tcategory : %s,\n" % self.category)
        str += ("\n}")
        return str

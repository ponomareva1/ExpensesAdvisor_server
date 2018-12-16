class ItemInfo:
    def __init__(self, record):
        self.name = record[0]
        self.price = record[1]
        self.quant = record[2]
        self.category = record[3]

    def __str__(self) -> str:
        str = "{\n"
        str += ("\tname : %s,\n" % self.name)
        str += ("\tprice : %s,\n" % self.price)
        str += ("\tquant : %s,\n" % self.quant)
        str += ("\tcategory : %s,\n" % self.category)
        str += ("\n}")
        return str

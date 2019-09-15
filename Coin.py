from GlobalVariable import *

class Coin:

    def __init__(self, name, orderbook, withdrawFee):
        self.name = name
        self.orderBook = orderbook
        try :
            self.precision = coin_precision[name]
        except : self.precision = 4

        self.withdrawFee = withdrawFee

        self.wannabuy = orderbook["wannabuy"]
        self.wannasell = orderbook["wannasell"]

    def __str__(self):
        return self.name
    def __repr__(self):
        return self.name


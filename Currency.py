from Coin import *
import GlobalVariable
import sys

class Currency :
    def __init__(self, name, marketName, coin_list, API):
        self.name = name
        self.marketName = marketName
        self.API = API
        self.coin_list = self.setCoinList(coin_list)



    def __str__(self):
        return self.name
    def __repr__(self):
        return self.name

    def setCoinList(self, coin_list):
        # set tradable coin list
        result = []

        for i in coin_list :
            try :
                withdrawalFee = GlobalVariable.marketWithdrawFee[self.marketName][i]
            except :
                print("    Currency(" + str(sys._getframe().f_lineno) + ") : "+self.name,"_",i + "_withdrawal fee error")
                continue

            try :
                result.append(Coin(i, self.API.GetOrderBook(self.name, i), withdrawalFee))
            except :
                print("    Currency(" + str(sys._getframe().f_lineno) + ") : " + self.name ,"_", i + "_ set Coin error")
                continue

        return result

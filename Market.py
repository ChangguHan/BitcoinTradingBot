from Coin import *
from Currency import *
import API
import GlobalVariable
import sys

class Account:
    def __init__(self, bal=None, wallet= None):
        self.Balance=bal
        self.WalletAddress=wallet        

class Market_Eq :
    def __init__(self, name,currency_name,coin_name):
        self.name=name
        if name == "Kucoin" :
            api = API.KucoinAPI()
        elif name == "Gate" :
            api = API.GateAPI()
        elif name == "Bithumb":
            api = API.BithumbAPI()
        elif name == "Coinnest" :
            api = API.CoinnestAPI()
        elif name == "Poloniex" :
            api = API.PoloniexAPI()
        elif name == "Gopax" :
            api = API.GopaxAPI()
        elif name == "Binance" :
            api = API.BinanceAPI()
        self.API= api
        self.tradeFee = GlobalVariable.marketTradeFee[self.name]
        self.currencyList = [Currency(currency_name, self.name, [coin_name], self.API)]

class Market_Ex :
    def __init__(self, name):
        self.name=name
        if name == "Kucoin" :
            api = API.KucoinAPI()
        elif name == "Gate" :
            api = API.GateAPI()
        elif name == "Bithumb":
            api = API.BithumbAPI()
        elif name == "Poloniex" :
            api = API.PoloniexAPI()
        elif name == "Gopax" :
            api = API.GopaxAPI()
        elif name == "Binance" :
            api = API.BinanceAPI()
        self.API= api
        self.tradeFee = GlobalVariable.marketTradeFee[self.name]
        # print("    Market(" + str(sys._getframe().f_lineno) + ") : (" + self.name + ") : currencylist start")

        self.currencyList = self.set_currency_list()

        print("    Market(" + str(sys._getframe().f_lineno) + ") : (" + self.name + ") : currencylist : ", self.currencyList)
        for i_currency in self.currencyList :
            print("    Market(" + str(sys._getframe().f_lineno) + ") : (" + self.name + ") : ",i_currency," : ",i_currency.coin_list)


        self.baseCurrencyMap = {}
        # For FCSMS_USDT_map in Simulation.py
        # When you use Korean market, You need to modify the number on hand
        for i in self.currencyList :
            if i.name == "KRW" :
                self.baseCurrencyMap[i.name] = {"wannabuy" : {1/1194.5 : 100000000}, "wannasell" : {1/1194.5 : 10000000}}
            else :
                if i.name == "USDT" : continue
                orderbook = self.API.GetOrderBook("USDT", i.name)
                self.baseCurrencyMap[i.name] = orderbook
        if self.API == None:
            print("    Market(" +str(sys._getframe().f_lineno) + ") : Error : API is not created")

    def set_currency_list(self):

        try :
            tickers = self.API.GetTickers()
        except :
            tickers = {}

        result = []
        # # USDT만 해보기, 너무 오래걸림, 이따 수정필요
        # try:
        #     result.append(Currency("USDT",self.name, tickers["USDT"], self.API))
        # except :
        #     print("    Market(" + str(sys._getframe().f_lineno) + ") : (" + self.name + ") : currency : " + "USDT", "Error")
        for i in list(tickers.keys()) :
            try :
                result.append(Currency(i,self.name, tickers[i], self.API))
            except :
                print("    Market(" + str(sys._getframe().f_lineno) + ") : (" + self.name + ") : currency : " + i, "Error")
        return result

    def __str__(self):
        return self.name
    def __repr__(self):
        return self.name

    def GetBookInfo(self):
        return self.API.GetOrderBook()

    def SetAPI(self, api):
        self.API= api
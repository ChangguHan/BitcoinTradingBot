import math
import sys

def precisionInOrderBook(orderBook, coin):
    result = {}
    for price in orderBook.keys():
        result[price] = math.floor(orderBook.get(price) * pow(10, coin.precision)) / pow(10, coin.precision)

    return result

def tradeAmountCheck(amount_price, currency_string) :
    result = True
    if currency_string == "BTC" :
        if amount_price < 0.001 : result = False
    elif currency_string == "USDT" :
        if amount_price < 1: result = False
    # in case of a Gate, You should trade more than 1$
    elif currency_string == "ETH" :
        if amount_price < 0.01: result = False
    return result

def getOrderBookInMoney(currency_string, coin, inputAmount, type):
    # get Order Book by input Amount
    result = {}
    money = inputAmount
    if type == "SELL":  # ""wannaBuy" : input coin amount on money
        try :
            orderBook = coin.wannabuy
        except :
            orderBook = coin['wannabuy']
        orderBook = dic_filter_toFloat(orderBook)
        key_sorting = list(orderBook.keys())
        key_sorting.sort()
        key_sorting.reverse()  # ascending order of price
    elif type == "BUY":  # ""wannaSell" :input money amouint on money
        try :
            orderBook = coin.wannasell
        except :
            orderBook = coin['wannasell']
        orderBook = dic_filter_toFloat(orderBook)
        key_sorting = list(orderBook.keys())
        key_sorting.sort()  # descending order of price

    for price_for in key_sorting:
        price_for = float(price_for)
        # Set minimum amount of price
        if not tradeAmountCheck(float(price_for)*float(orderBook.get(price_for)), currency_string) : continue
        if not tradeAmountCheck(money, currency_string) :
            print("        GlobalM(" + str(sys._getframe().f_lineno) + ") : No money : " + str(money))
            break

        if type == "BUY" : #"wannaSell":

            if money <= (price_for * float(orderBook.get(price_for))):  # If the sum of orderbook is more than money
                # The amount you can buy
                amount = money / price_for
                # If there are more orderbook than you can buy
                if not tradeAmountCheck(float(price_for)*amount, currency_string): continue  #넘어가기
                result[price_for] = amount
                break
            else:  # If you buy all and have money more
                amount = float(orderBook.get(price_for))
                result[price_for] = amount
                money -= (price_for * amount)
        elif type == "SELL" : #"wannaBuy":

            if money < (price_for * (orderBook.get(price_for))):  # 호가창에 올라온게 더 많으면
                amount = money / price_for
                if not tradeAmountCheck(float(price_for)*amount, currency_string): continue
                result[price_for] = amount
                break
            else:  # If you sell all and also have some coin
                amount = float(orderBook[price_for])
                result[price_for] = amount
                money -= (amount * price_for)


    try : result = precisionInOrderBook(result, coin)
    except : result = result

    for i in list(result.keys()) :
        if not tradeAmountCheck(float(i)*float(result[i]), currency_string): return {0:0}

    return result

def getOrderBookInMoney_coinAmount(currency_string, coin, inputAmount, type):
    # Get Orderbook by coin amount
    result = {}
    money = inputAmount
    if type == "SELL":  # ""wannaBuy" : money<-Coin Amount
        try :
            orderBook = coin.wannabuy
        except :
            orderBook = coin['wannabuy']
        orderBook = dic_filter_toFloat(orderBook)
        key_sorting = list(orderBook.keys())
        key_sorting.sort()
        key_sorting.reverse()  # 비싼 순서대로 key 정렬
    elif type == "BUY":  # ""wannaSell" :money <-Coin Amount
        try :
            orderBook = coin.wannasell
        except :
            orderBook = coin['wannasell']
        orderBook = dic_filter_toFloat(orderBook)
        # print("GlobalMethod.orderBook", orderBook)
        key_sorting = list(orderBook.keys())
        key_sorting.sort()  # descending order

    for price_for in key_sorting:
        price_for = float(price_for)
        # Set minimum trade amount
        if not tradeAmountCheck(float(price_for)*float(orderBook.get(price_for)), currency_string) : continue
        if not tradeAmountCheck(float(price_for) * money, currency_string):
            print("        GlobalM(" + str(sys._getframe().f_lineno) + ") : No Coin : " + str(money))
            break


        if type == "BUY" : #"wannaSell":

            if money <= (float(orderBook.get(price_for))):  # 호가창에 올라온게 더 많다면
                amount = money
                if not tradeAmountCheck(float(price_for)*amount, currency_string): continue
                result[price_for] = amount
                break
            else:  # If you buy all and you have also money
                amount = float(orderBook.get(price_for))
                result[price_for] = amount
                money -=  amount
        elif type == "SELL" : #"wannaBuy":

            if money < float(orderBook.get(price_for)):  # Order book money > your money
                amount = money
                if not tradeAmountCheck(float(price_for)*amount, currency_string): continue
                result[price_for] = amount
                break
            else:  # If you sell all and you have also
                amount = float(orderBook[price_for])
                result[price_for] = amount
                money -= amount


    try : result = precisionInOrderBook(result, coin)
    except : result = result

    for i in list(result.keys()) :
        if not tradeAmountCheck(float(i)*float(result[i]), currency_string): return {0:0}

    return result


def sorting(lists):
    # descending order and return first value
    lists.sort()
    lists.reverse()
    return lists[0]
def sortings(lists,number):
    # descending order and return first value
    lists.sort()
    lists.reverse()
    return lists[number]


def tradeableCoinList(market1, market2):
    tradeableCoinList = {}
    market1_dic = {}
    market2_dic = {}

    # gather coin in market 1, 2
    market1_coinList = []
    for currency_market1_for in market1.currencyList:
        for coin_market1_for in currency_market1_for.coin_list:
            if not market1_coinList.count(coin_market1_for.name):
                market1_coinList.append(coin_market1_for.name)
    # print("market1_coinList")
    # print(market1_coinList)

    market2_coinList = []
    for currency_market2_for in market2.currencyList:
        for coin_market2_for in currency_market2_for.coin_list:
            if not market2_coinList.count(coin_market2_for.name):
                market2_coinList.append(coin_market2_for.name)
    # print("market2_coinList")
    # print(market2_coinList)

    # make intersection list of coin
    market_common_coinList = []
    for market1_coin_for in market1_coinList:
        if market2_coinList.count(market1_coin_for):
            market_common_coinList.append(market1_coin_for)

    for currency_market1_for2 in market1.currencyList:
        currency_market1_coinList = []
        for coin_market1_for2 in currency_market1_for2.coin_list:
            if market_common_coinList.count(coin_market1_for2.name):
                if not currency_market1_for2.name == coin_market1_for.name:
                    currency_market1_coinList.append(coin_market1_for2)
        market1_dic[currency_market1_for2] = currency_market1_coinList

    for currency_market2_for2 in market2.currencyList:
        currency_market2_coinList = []
        for coin_market2_for2 in currency_market2_for2.coin_list:
            if market_common_coinList.count(coin_market2_for2.name):
                if not currency_market2_for2.name == coin_market2_for.name:
                    currency_market2_coinList.append(coin_market2_for2)
        market2_dic[currency_market2_for2] = currency_market2_coinList

    tradeableCoinList[market1] = market1_dic
    tradeableCoinList[market2] = market2_dic

    return tradeableCoinList


def find_object_in_list_by_name(list, name):
    count = 0
    for i in list:
        if i.name == name:
            result = i
            count = count + 1
    if count > 1 or count == 0:
        # print("Sim30) Error")
        # print(list)
        # print(name)
        exit()
    return result


def listSum(list):
    result = 0
    for i in list :
        result += i
    return result

def keyValueSum(Dic):
    result = 0
    for i in list(Dic.keys()) :
        result += i * Dic[i]
    return result

def dic_filter_toFloat(dic):
    result = {}
    for i in list(dic.keys()) :
        result[float(i)] = float(dic[i])
    return result

def checkBalance(Market, coin_name) :
    return float(Market.API.GetBalance()[coin_name])


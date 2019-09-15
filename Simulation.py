from Market import *
from GlobalVariable import *
from GlobalMethod import *
import sys

class Simulation :
    def __init__(self, mBase, m_lmarketlist, startCurrencyString, inputMoney):
        # market List Check again
        self.market_list = []
        for i in m_lmarketlist :
            if not i.name == mBase.name : self.market_list.append(i)
        self.mBase = mBase
        self.inputMoney = inputMoney

        # Find Start currency Object
        for currency_for in mBase.currencyList :
            if currency_for.name == startCurrencyString :
                self.startCurrency = currency_for

        # Calculation
        self.result_cal1 = self.calculation()
        print(self.result_cal1)
        self.result_sim1 = self.simulation1(self.result_cal1)
        self.result_coinSorting = self.coinSorting(self.result_cal1)


        for market_for in m_lmarketlist :
            if market_for.name == self.result_sim1['market2'] :
                self.market2 = market_for

    def calculation(self) :
        mBase = self.mBase
        m_lmarketlist = self.market_list
        startCurrency = self.startCurrency
        inputMoney = self.inputMoney

        result = {}
        result_profit = {}
        result_details = {}
        result_firstEx = {}
        result_secondEx = {}

        # Calculation for market
        for mSub in m_lmarketlist:
            # Check tradable coin
            tradeableCoinList_Dic = tradeableCoinList(mBase, mSub)
            # Check tradable Currency for the tradable coin(upper)
            market1_CurrencyList = list(tradeableCoinList_Dic[mBase].keys())
            market2_CurrencyList = list(tradeableCoinList_Dic[mSub].keys())

            # Calculation Start
            for currency_first in market1_CurrencyList :
                # You should purchase the currency for buying the first coin
                # FCuFMB means First Currency First Market Buy
                if currency_first.name == startCurrency.name :
                    FCuFMB_map = {}
                    FCuFMB_result = inputMoney
                # or we should buy some currency from the currency which first we start
                else :
                    try:
                        currency_first_coin = find_object_in_list_by_name(self.startCurrency.coin_list,
                                                                               currency_first.name)
                    except:
                        continue
                    FCuFMB_map = getOrderBookInMoney(self.startCurrency.name, currency_first_coin, inputMoney, "BUY")
                    FCuFMB_result = listSum(FCuFMB_map.values()) * (1-mBase.tradeFee)

                # Check tradeable coin List for each currency
                market1_CoinList = tradeableCoinList_Dic[mBase][currency_first]

                # Buy First Coin in First Market
                for FirstCoin in market1_CoinList:
                    # There is some trouble coin when you run this program
                    # You can add the coin in GlobalVarialble.py
                    if notWithdrawCoin[mBase.name].count(FirstCoin.name) : continue
                    # FCFMB means First Coin First Market Buy
                    FCFMB_map = getOrderBookInMoney(currency_first.name, FirstCoin, FCuFMB_result, "BUY")
                    FCFMB_result = listSum(FCFMB_map.values()) * (1 - mBase.tradeFee) - FirstCoin.withdrawFee

                    # Sell First Coin in Second Market
                    for currency_second in market2_CurrencyList:
                        market2_CoinList = tradeableCoinList_Dic[mSub][currency_second]
                        # If there are some case that First Coin and Second Currency are same, Just pass
                        if FirstCoin.name == currency_second.name :
                            # FCSMS means First Coin Second Market Sell
                            FCSMS_map = {}
                            FCSMS_result = FCFMB_result
                        else :
                            try :
                                firstcoin_market2 = find_object_in_list_by_name(currency_second.coin_list, FirstCoin.name)
                            except :
                                continue
                            FCSMS_map = getOrderBookInMoney_coinAmount(currency_second.name, firstcoin_market2, FCFMB_result, "SELL")
                            FCSMS_result = keyValueSum(FCSMS_map) * (1 - mSub.tradeFee)


                        # Check the middle profit which buy first coin and sell in second market
                        try :
                            if not currency_second.name == "USDT" :
                                FCSMS_USDT_map = getOrderBookInMoney("USDT", mSub.baseCurrencyMap[currency_second.name], FCSMS_result, "SELL")
                                FCSMS_USDT_result = keyValueSum(FCSMS_USDT_map)

                            else :
                                FCSMS_USDT_map = {}
                                FCSMS_USDT_result = FCSMS_result
                        except : continue

                        for SecondCoin in market2_CoinList:
                            # Check not some trouble coin
                            if notWithdrawCoin[mSub.name].count(SecondCoin.name): continue

                            # SCSMB means Second Coin Second Market Buy
                            if currency_second.name == SecondCoin.name :
                                SCSMB_map = {}
                                SCSMB_result = FCSMS_result
                            else :
                                SCSMB_map = getOrderBookInMoney(currency_second.name, SecondCoin, FCSMS_result, "BUY")
                                SCSMB_result = listSum(SCSMB_map.values()) * (1 - mSub.tradeFee) - SecondCoin.withdrawFee


                            for currency_third in mBase.currencyList:
                                # print("            Sim(" + str(sys._getframe().f_lineno) + ") : " + currency_third.name)
                                try:
                                    secondCoin_market1 = find_object_in_list_by_name(currency_third.coin_list,
                                                                                          SecondCoin.name)
                                except:
                                    continue

                                SCFMS_map = getOrderBookInMoney_coinAmount(currency_third.name, secondCoin_market1,
                                                                     SCSMB_result, "SELL")
                                SCFMS_result = keyValueSum(SCFMS_map) * (1 - mBase.tradeFee)

                                # SCuFMS means Second Currency First Market Sell
                                if currency_third.name == startCurrency.name:
                                    SCuFMS_map = {}
                                    SCuFMS_result = SCFMS_result
                                else:

                                    try:
                                        currency_third_coin = find_object_in_list_by_name(self.startCurrency.coin_list,
                                                                                              currency_third.name)
                                    except:
                                        continue

                                    SCuFMS_map = getOrderBookInMoney_coinAmount(self.startCurrency.name, currency_third_coin,
                                                                          SCFMS_result, "SELL")
                                    SCuFMS_result = keyValueSum(SCuFMS_map) * (1 - mBase.tradeFee)


                                profit = SCuFMS_result / inputMoney;
                                profit = round(profit,4)
                                result_profit[mBase.name + "-" + mSub.name + "-" + currency_first.name + "-" + FirstCoin.name +"-"+ currency_second.name + "-" + SecondCoin.name +"-"+ currency_third.name] = profit
                                details = {}
                                try :
                                    details["FirstEx"] = round(FCSMS_USDT_result/inputMoney,4)
                                    details["SecondEx"] = round(SCuFMS_result / FCSMS_USDT_result,4)
                                except :
                                    details["FirstEx"] = 0
                                    details["SecondEx"] = 0
                                result_firstEx[
                                    mBase.name + "-" + mSub.name + "-" + currency_first.name + "-" + FirstCoin.name + "-" + currency_second.name + "-" + SecondCoin.name + "-" + currency_third.name] = details["FirstEx"]
                                result_secondEx[
                                    mBase.name + "-" + mSub.name + "-" + currency_first.name + "-" + FirstCoin.name + "-" + currency_second.name + "-" + SecondCoin.name + "-" + currency_third.name] = details["SecondEx"]
                                details["FCuFMB_map"] = FCuFMB_map
                                details["FCuFMB_result"] = FCuFMB_result
                                details["FCFMB_map"] =  FCFMB_map
                                details["FCFMB_result"] = FCFMB_result
                                details["FCSMS_map"] = FCSMS_map
                                details["FCSMS_result"] = FCSMS_result
                                details["FCSMS_USDT_map"] = FCSMS_USDT_map
                                details["FCSMS_USDT_result"] = FCSMS_USDT_result
                                details["SCSMB_map"] = SCSMB_map
                                details["SCSMB_result"] = SCSMB_result
                                details["SCFMS_map"] = SCFMS_map
                                details["SCFMS_result"] = SCFMS_result
                                details["SCuFMS_map"] = SCuFMS_map
                                details["SCuFMS_result"] = SCuFMS_result

                                result_details[
                                    mBase.name + "-" + mSub.name + "-" + currency_first.name + "-" + FirstCoin.name + "-" + currency_second.name + "-" + SecondCoin.name + "-" + currency_third.name] = details

                                result["profit"] = result_profit
                                result["FirstEx"] = result_firstEx
                                result["SecondEx"] = result_secondEx
                                result["details"] = result_details
                                result["firstCoin"] = FirstCoin.name
                                result["secondCoin"] = SecondCoin.name


        return result

    def coinSorting(self, calculation_result):

        result = {}


        for market in self.market_list :
            # print(self.market_list)
            # print(market)
            result_firstEx = {}
            result_secondEx = {}
            coinList = tradeCoinList[market.name]
            for i in coinList :
                result_firstEx[i] = [0,""]
                result_secondEx[i] = [0,""]

            for key in calculation_result["FirstEx"].keys() :
                if key.split("-")[1] == market.name :
                    if calculation_result["FirstEx"][key] > result_firstEx[key.split("-")[3]][0] :
                        result_firstEx[key.split("-")[3]] = [calculation_result["FirstEx"][key], key]

            for key2 in calculation_result["SecondEx"].keys() :
                if key2.split("-")[1] == market.name:
                    if calculation_result["SecondEx"][key2] > result_secondEx[key2.split("-")[5]][0] :
                        result_secondEx[key2.split("-")[5]] = [calculation_result["SecondEx"][key2], key2]

            result[market.name] = {"first" : result_firstEx, "second" : result_secondEx}


        return result






    def simulation1(self, calculation_result):
        result = {}

        profit = sorting(list(calculation_result["profit"].values()))
        for key in calculation_result['profit'].keys():
            if calculation_result["profit"][key] == profit:
                max_profit_key = key
                break
        market2_name = max_profit_key.split("-")[1]
        currency_first = max_profit_key.split("-")[2]
        currency_second = max_profit_key.split("-")[4]
        currency_third = max_profit_key.split("-")[6]
        firstCoin = max_profit_key.split("-")[3]
        secondCoin = max_profit_key.split("-")[5]



        result["profit"] = profit
        result["market2"] = market2_name
        result["currency_first"] = currency_first
        result["currency_second"] = currency_second
        result["currency_third"] = currency_third
        result["firstCoin"] = firstCoin
        result["secondCoin"] = secondCoin
        result["details"] = calculation_result["details"][max_profit_key]
        return result


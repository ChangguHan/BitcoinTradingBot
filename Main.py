# In this, You need to run

from Market import *
from Simulation import *
import GlobalVariable
from Log import *
from Mail import *


# Setting Market Instance
while True:

    # Make Log instance
    log = Log()

    #####You need set##########
    # Set profit which you want trade
    profit = 1.025;
    # Set your base money to run(USDT)
    base_money = 1000;
    # Set your e-mail address but you need to use g-mail
    mail_ID = "cottage123@gmail.com"
    mail_PW = "**********"
    # Set your base market
    base_market = "Gate"
    # Set your market List
    # Now "Kucoin" is available
    insertMarketList = ["Kucoin"]#["Kucoin", "Poloniex", "Binance", "Bithumb", "Gopax]
    ############################


    # 'i' is need to make new log file
    i = 0
    while True:
        # market1 is your base coin_market
        print("Main(" + str(sys._getframe().f_lineno) + ") : Market Setting...")
        try:
            market1 = Market_Ex(base_market)
            print("Main(" + str(sys._getframe().f_lineno) + ") : Market(" + base_market + ")_Complete")
        except :
            print("Main(" + str(sys._getframe().f_lineno) + ") : Market("+ base_market +")_Error")

        # market_List is list of markets to exchange
        # In this "Kucoin"... are available.
        market_List = []
        for i_market in insertMarketList :
            try:
                market_List.append(Market_Ex(i_market))
                print("Main(" + str(sys._getframe().f_lineno) + ") : Market(",i_market,")_Complete")

            except:
                print("Main(" + str(sys._getframe().f_lineno) + ") : Market(",i_market,")_Error")

        # Sim is class of Calculate profit
        Sim = Simulation(market1, market_List, "USDT", base_money)

        try :
            log.writeCalculation(Sim.result_sim1)
            log.writeCoinSorting(Sim.result_coinSorting)
        except : print("log Err")
        print("\n===================================\n")

        if Sim.result_sim1['profit'] >= profit:
            # Mail to your address
            mail_subect = "Profit : " + str(Sim.result_sim1['profit']) + " ( " + str(
                Sim.result_sim1['details']['FirstEx']) + " / " + str(Sim.result_sim1['details']['SecondEx']) + " )"
            mail_message = Sim.result_sim1['market2'] + " : " +Sim.result_sim1['currency_first'] + "-" + Sim.result_sim1['firstCoin'] + "-" + Sim.result_sim1['currency_second'] + "-" + Sim.result_sim1['secondCoin'] + "-" + Sim.result_sim1['currency_third']
            profitMail = Mail(mail_subect,mail_ID,mail_PW,mail_message)

        i = i + 1
        if i > 10: break

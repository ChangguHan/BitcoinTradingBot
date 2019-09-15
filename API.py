import GlobalVariable
import json
import requests
import time
import base64
import hashlib
import hmac
from urllib.parse import urljoin
import urllib.parse
import sys
import datetime, time

class BaseAPI:
    def __init__(self, pub, priv):
        self.private_key=priv
        self.public_key=pub
        self.BaseURL=None
        self.session = self._init_session()


    def GetTickers(self):
        raise NotImplementedError(__name__+ ": The method not implemented")

    def GetOrderBook(self):
        raise NotImplementedError(__name__+ ": The method not implemented")

    def GetBalance(self):
        raise NotImplementedError(__name__+ ": The method not implemented")

    def GetDepositAddress(self):
        raise NotImplementedError(__name__+ ": The method not implemented")

    def GetBuyOrder(self):
        raise NotImplementedError(__name__+ ": The method not implemented")

    def GetSellOrder(self):
        raise NotImplementedError(__name__+ ": The method not implemented")

    def GetOpenOrderCheck(self):
        raise NotImplementedError(__name__+ ": The method not implemented")

    def GetCancelOrders(self):
        raise NotImplementedError(__name__+ ": The method not implemented")

    def GetWithdrawal(self):
        raise NotImplementedError(__name__+ ": The method not implemented")

    def _getNonce(self):
        nonce = int(time.time() * 1000)
        return str(nonce)


class BxinthAPI(BaseAPI):

    def __init__(self):
        self.name = "Bxinth"
        self.paring = {}


        BaseAPI.__init__(self, "", "")
        self.BaseURL="https://bx.in.th/api"

    def _init_session(self):
        session = requests.session()
        return session

    def _getNonce(self):
        nonce = int(time.mktime(datetime.datetime.now().timetuple()) * 1000)

        return str(nonce)

    def _request(self, method, path, headNeed, **kwargs) :
        kwargs['data'] = kwargs.get('data', {})
        kwargs['headers'] = kwargs.get('headers',{})

        if kwargs['data'] and method == 'get':
            uri = self.BaseURL + path + "?" + self._order_params_for_sig(kwargs['data'])
        else : uri = self.BaseURL + path
        nonce = self._getNonce()
        if headNeed :
            kwargs['headers']['KC-API-KEY'] = self.public_key
            kwargs['headers']['KC-API-TIMESTAMP'] = nonce
            kwargs['headers']['KC-API-SIGN'] =self._generate_signature(path,method.upper(), kwargs['data'], nonce)
            kwargs['headers']['KC-API-PASSPHRASE'] = "" #passward
            kwargs['headers']['Content-Type'] = "application/json"



        if not kwargs['data'] == {} : kwargs['data'] = json.dumps(kwargs['data'])
        # if method == 'post' :kwargs['data'] = json.dumps(kwargs['data'])
        # kwargs['data'] = json.dumps(kwargs['data'])
        try : response = requests.request(method,uri, headers = kwargs['headers'],data = kwargs['data'])
        except : print("response error")
        result = response.json()
        # print("        API(" + str(sys._getframe().f_lineno) + ") : " , result)
        return result


    def _generate_signature(self, path, method, data, nonce) :


        if (data != {}) and method == 'GET':
            path = path + "?" + self._order_params_for_sig(data)


        if data == {}: query_string = nonce + method + path
        else : query_string = nonce + method + path + json.dumps(data)

        # if method == "GET" :query_string = nonce + method + path + json.dumps(data)
        # else :
        #     query_string = nonce + method + path + json.dumps(data)




        signature = base64.b64encode(
            hmac.new(self.private_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).digest())
        return signature


    def _order_params_for_sig(self, data):
        strs = []
        for key in sorted(data) :
            strs.append("{}={}".format(key, data[key]))
        return '&'.join(strs)

    def GetTickers(self):
        path = "/"
        kwargs = {}
        result = {}

        try :
            response_before = self._request('get', path, False, **kwargs)
            response = response_before
        except :
            print("        API(" + str(sys._getframe().f_lineno) + ")")
            response = []
        self.paring = {}
        for i in response :
            response_i = response[i]
            if GlobalVariable.notTradeCoinList.count(response_i["secondary_currency"]) :
                print("        API(" + str(sys._getframe().f_lineno) +") : Not tradable Coin")
                continue
            if not list(result.keys()).count(response_i["primary_currency"]) :
                result[response_i["primary_currency"]] = [response_i["secondary_currency"]]
                self.paring[response_i["primary_currency"]] = {
                    response_i["secondary_currency"]: response_i["pairing_id"]}
            else :
                if not response_i["primary_currency"] == response_i["secondary_currency"] :
                    result[response_i["primary_currency"]].append(response_i["secondary_currency"])
                self.paring[response_i["primary_currency"]][response_i["secondary_currency"]] = response_i["pairing_id"]


        # # V1_1 임시추가
        # # TradeCoinList에 있는지 다시한번 체크
        # result2 = {}
        # for key_result in result:
        #     for value_result in result[key_result]:
        #         if GlobalVariable.tradeCoinList[self.name].count(value_result):
        #             try :
        #                 result2[key_result].append(value_result)
        #             except :
        #                 result2[key_result] = [value_result]
        #
        # result = result2
        return result


    def GetOrderBook(self, currency_string, coin_string):
        path = "/orderbook/?paring=" + str(self.paring[currency_string][coin_string])
        kwargs = {}
        result = {}
        wannasell = {}
        wannabuy = {}
        if currency_string == coin_string :
            result["wannabuy"] = wannabuy
            result["wannasell"] = wannasell
            return result
        try :
            response = self._request('get', path, False, **kwargs)
            if response["bids"]:
                for i in response["bids"]:
                    wannabuy[i[0]] = i[1]
            if response["asks"]:
                for j in response["asks"]:
                    wannasell[j[0]] = j[1]
            result["wannabuy"] = wannabuy
            result["wannasell"] = wannasell
        except : return result

        return result


    def GetBalance(self):
        path = "/api/v1/accounts"
        kwargs = {}
        result = {}
        try :
            response_before = self._request('get', path, True, **kwargs)
            response = response_before['data']
        except :
            try:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Balance Error / Message : ",
                      response_before)
            except:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Balance Error")
            quit()

        for i in response :
            try : result[i['currency']] += float(i['available'])
            except : result[i['currency']] = float(i['available'])
        return result

    def GetDepositAddress(self, coin_string):
        path = "/api/v1/deposit-addresses"
        kwargs = {"data" : {"currency" : coin_string}}
        response = {}
        try :
            response_before =self._request('get', path, True,**kwargs)
            response['address'] = response_before['data']['address']
            if not response_before['data']['memo'] == '' : response['memo'] =response_before['data']['memo']

        except :
            try:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Deposit Address / Message : ",
                      response_before)
            except:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Deposit Address Error")
            return False


        return response

    def GetOpenOrderCheck(self, currency_string, coin_string):
        # 결과를 가격, 갯수로 나타내고싶은데 이건 실제 order 올려보고 수정해야함
        path = "/api/v1/orders"
        kwargs = {'data' : {"status" : "active" ,"symbol" : coin_string +"-" +  currency_string}}
        result = {}
        try :
            response_before = self._request('get', path, True,**kwargs)
            response = response_before['data']
            # print(response_before)

        except :
            try:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Open Order Check Error / Message : ",
                      response_before)
            except:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Open Order Check Error")

        for i in response['items'] :
            try : result[float(i['price'])] = float(i['size'])
            except : result = {}
        return result

    def GetCancelOrders(self, currency_string, coin_string):
        path = "/api/v1/orders"
        kwargs = {'data': {"symbol": coin_string + "-" + currency_string}}
        try :
            response_before =self._request( 'delete', path,True, **kwargs)
            response = response_before['data']
        except :
            try:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Cancel Order Error / Message : ",
                      response_before)
            except:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Cancel Order Error")
            return False
        result = True
        print("        API(" + str(sys._getframe().f_lineno) + ") : ", len(response['cancelledOrderIds']), "Deleted")

        return result

    def GetBuyOrder(self, currency_string, coin_string, amount, price):
        path = "/api/v1/orders"
        kwargs = {'data': {"clientOid":"Django" + str(time.time()),"side" : "buy", "symbol": coin_string + "-" + currency_string, "type" : "limit", "price" : price, "size" : amount }}
        try :
            response_before = self._request('post', path, True,**kwargs)
            response = response_before['code']#['success'] # true(성공값)
        except :
            try:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Buy Order Error / Message : ",
                      response_before)
                return False
            except:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Buy Order Error")
            return False
        # True일때 나오는거 확인해봐야함

        result = False
        if (response == str(200000)) or  (response == str(200)):
            result = True
        else : print("        API(" + str(sys._getframe().f_lineno) + ") ", response_before)


        return result

    def GetSellOrder(self, currency_string, coin_string, amount, price):
        path = "/api/v1/orders"
        kwargs = {'data': {"clientOid":"Django" + str(time.time()),"side" : "sell", "symbol": coin_string + "-" + currency_string, "type" : "limit", "price" : price, "size" : amount }}
        try :
            response_before =self._request('post', path,True, **kwargs)
            response = response_before['code'] #['success'] # true(성공값)
        except :
            try : print("        API(" + str(sys._getframe().f_lineno) + ") Get Sell Order Error / Message : ",response_before)
            except : print("        API(" + str(sys._getframe().f_lineno) + ") Get Sell Order Error")
            return False
        # True일때 나오는거 확인해봐야함
        result = False

        if (response == str(200000)) or  (response == str(200)):
            result = True
        else : print("        API(" + str(sys._getframe().f_lineno) + ") ", response_before)

        return result


    def GetWithdrawal(self, coin_string, amount, address):
        path = "/api/v1/withdrawals"

        if not self.GetTransfer(coin_string, amount, "trade","main") :
            print("        API(" + str(sys._getframe().f_lineno) + ") Get Withdrawal Error / Transfer Error")
            quit()

        kwargs = {'data': {"currency" : coin_string, "address" : address['address'], "amount" : amount }}
        try : kwargs['data']['memo'] = address['memo']
        except : kwargs['data']['address'] = address['address']

        try :
            response_before =self._request('post', path,True, **kwargs)
            response = response_before['code'] # ['success'] # true(성공값)
        except :
            try:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Withdrawal Error / Message : ",
                      response_before)
            except:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Withdrawal Error")

            return False

        result = False
        if response == str(200000) :
            result = True

        return result

    def CreateAccounts(self, coin_string, type):
        path = "/api/v1/accounts"
        kwargs = {'data': {"type" : type, "currency": coin_string}}
        try :
            response_before =self._request('post', path,True, **kwargs)
            response = response_before['data']['id']

        except:
            try:
                print("        API(" + str(sys._getframe().f_lineno) + ") Create Accounts Error / Message : ",
                      response_before)
            except:
                print("        API(" + str(sys._getframe().f_lineno) + ") Create Accounts Error")
                return {}



        return response

    def GetAccounts(self, coin_string):
        path = "/api/v1/accounts"
        kwargs = {'data': {"currency": coin_string}}
        try :
            response_before =self._request('get', path,True, **kwargs)
            response = response_before['data']
            # trade나 main 중 하나밖에 없으면 위에서 생성
        except :
            try:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Accounts Error / Message : ",
                      response_before)
            except:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Accounts Error")

            return {}

        result = {}
        for i in response :
            result[i['type']] = i['id']

        return result

    def GetTransfer(self, coin_string, amount,fromType,toType):
        path = "/api/v1/accounts/inner-transfer"
        accountInfo = self.GetAccounts(coin_string)
        kwargs = {'data': {"clientOid": "Django" + str(time.time()), "payAccountId": accountInfo[fromType], "recAccountId": accountInfo[toType], "amount": amount}}

        #
        #
        try :
            response_before =self._request('post', path,True, **kwargs)
            print(response_before )
            response = response_before['data']
            # trade나 main 중 하나밖에 없으면 위에서 생성
        except :
            try:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Transfer Error / Message : ",
                      response_before)
            except:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Transfer Error")

            return False

        return True





class KucoinAPI(BaseAPI):

    def __init__(self):
        self.name = "Kucoin"


        BaseAPI.__init__(self, GlobalVariable.keyPair[GlobalVariable.marketList[1]][0], GlobalVariable.keyPair[GlobalVariable.marketList[1]][1])
        self.BaseURL="https://openapi-v2.kucoin.com"

    def _init_session(self):
        session = requests.session()
        return session

    def _getNonce(self):
        nonce = int(time.mktime(datetime.datetime.now().timetuple()) * 1000)

        return str(nonce)

    def _request(self, method, path, headNeed, **kwargs) :
        kwargs['data'] = kwargs.get('data', {})
        kwargs['headers'] = kwargs.get('headers',{})

        if kwargs['data'] and method == 'get':
            uri = self.BaseURL + path + "?" + self._order_params_for_sig(kwargs['data'])
        else : uri = self.BaseURL + path
        nonce = self._getNonce()
        if headNeed :
            kwargs['headers']['KC-API-KEY'] = self.public_key
            kwargs['headers']['KC-API-TIMESTAMP'] = nonce
            kwargs['headers']['KC-API-SIGN'] =self._generate_signature(path,method.upper(), kwargs['data'], nonce)
            kwargs['headers']['KC-API-PASSPHRASE'] = "" #password
            kwargs['headers']['Content-Type'] = "application/json"



        if not kwargs['data'] == {} : kwargs['data'] = json.dumps(kwargs['data'])
        # if method == 'post' :kwargs['data'] = json.dumps(kwargs['data'])
        # kwargs['data'] = json.dumps(kwargs['data'])
        try : response = requests.request(method,uri, headers = kwargs['headers'],data = kwargs['data'])
        except : print("response error")
        result = response.json()
        # print("        API(" + str(sys._getframe().f_lineno) + ") : " , result)
        return result


    def _generate_signature(self, path, method, data, nonce) :


        if (data != {}) and method == 'GET':
            path = path + "?" + self._order_params_for_sig(data)


        if data == {}: query_string = nonce + method + path
        else : query_string = nonce + method + path + json.dumps(data)

        # if method == "GET" :query_string = nonce + method + path + json.dumps(data)
        # else :
        #     query_string = nonce + method + path + json.dumps(data)




        signature = base64.b64encode(
            hmac.new(self.private_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).digest())
        return signature


    def _order_params_for_sig(self, data):
        strs = []
        for key in sorted(data) :
            strs.append("{}={}".format(key, data[key]))
        return '&'.join(strs)

    def GetTickers(self):
        path = "/api/v1/symbols"
        kwargs = {}
        result = {}

        try :
            response_before = self._request('get', path, False, **kwargs)
            response = response_before["data"]
        except :
            print("        API(" + str(sys._getframe().f_lineno) + ")")
            response = []

        for i in response :
            if GlobalVariable.notTradeCoinList.count(i["symbol"].split("-")[0]) :
                print("        API(" + str(sys._getframe().f_lineno) +")")
                continue
            if not list(result.keys()).count(i["symbol"].split("-")[1]) :
                if not i["symbol"].split("-")[1] == i["symbol"].split("-")[0] :
                    result[i["symbol"].split("-")[1]] = [i["symbol"].split("-")[0]]
            else :
                if not i["symbol"].split("-")[1] == i["symbol"].split("-")[0] :
                    result[i["symbol"].split("-")[1]].append(i["symbol"].split("-")[0])
                # print("Tickers ( Kucoin )")



        # V1_1 임시추가
        result2 = {}
        for key_result in result:
            for value_result in result[key_result]:
                if GlobalVariable.tradeCoinList[self.name].count(value_result):
                    try :
                        result2[key_result].append(value_result)
                    except :
                        result2[key_result] = [value_result]

        result = result2
        return result


    def GetOrderBook(self, currency_string, coin_string):

        path = "/api/v1/market/orderbook/level2?symbol=" + coin_string + "-" + currency_string

        kwargs = {}
        result = {}
        wannasell = {}
        wannabuy = {}
        if currency_string == coin_string :
            result["wannabuy"] = wannabuy
            result["wannasell"] = wannasell
            return result
        try :
            response_before = self._request('get', path, False, **kwargs)
            response = response_before["data"]
            if response["bids"]:
                for i in response["bids"]:
                    wannabuy[i[0]] = i[1]
            if response["asks"]:
                for j in response["asks"]:
                    wannasell[j[0]] = j[1]
            result["wannabuy"] = wannabuy
            result["wannasell"] = wannasell
        except : return result

        return result


    def GetBalance(self):
        path = "/api/v1/accounts"
        kwargs = {}
        result = {}
        try :
            response_before = self._request('get', path, True, **kwargs)
            response = response_before['data']
        except :
            try:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Balance Error / Message : ",
                      response_before)
            except:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Balance Error")
            quit()

        for i in response :
            try : result[i['currency']] += float(i['available'])
            except : result[i['currency']] = float(i['available'])
        return result

    def GetDepositAddress(self, coin_string):
        path = "/api/v1/deposit-addresses"
        kwargs = {"data" : {"currency" : coin_string}}
        response = {}
        try :
            response_before =self._request('get', path, True,**kwargs)
            response['address'] = response_before['data']['address']
            if not response_before['data']['memo'] == '' : response['memo'] =response_before['data']['memo']

        except :
            try:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Deposit Address / Message : ",
                      response_before)
            except:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Deposit Address Error")
            return False


        return response

    def GetOpenOrderCheck(self, currency_string, coin_string):
        # 결과를 가격, 갯수로 나타내고싶은데 이건 실제 order 올려보고 수정해야함
        path = "/api/v1/orders"
        kwargs = {'data' : {"status" : "active" ,"symbol" : coin_string +"-" +  currency_string}}
        result = {}
        try :
            response_before = self._request('get', path, True,**kwargs)
            response = response_before['data']
            # print(response_before)

        except :
            try:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Open Order Check Error / Message : ",
                      response_before)
            except:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Open Order Check Error")

        for i in response['items'] :
            try : result[float(i['price'])] = float(i['size'])
            except : result = {}
        return result

    def GetCancelOrders(self, currency_string, coin_string):
        path = "/api/v1/orders"
        kwargs = {'data': {"symbol": coin_string + "-" + currency_string}}
        try :
            response_before =self._request( 'delete', path,True, **kwargs)
            response = response_before['data']
        except :
            try:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Cancel Order Error / Message : ",
                      response_before)
            except:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Cancel Order Error")
            return False
        result = True
        print("        API(" + str(sys._getframe().f_lineno) + ") : ", len(response['cancelledOrderIds']), "Deleted")

        return result

    def GetBuyOrder(self, currency_string, coin_string, amount, price):
        path = "/api/v1/orders"
        kwargs = {'data': {"clientOid":"Django" + str(time.time()),"side" : "buy", "symbol": coin_string + "-" + currency_string, "type" : "limit", "price" : price, "size" : amount }}
        try :
            response_before = self._request('post', path, True,**kwargs)
            response = response_before['code']#['success'] # true(성공값)
        except :
            try:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Buy Order Error / Message : ",
                      response_before)
                return False
            except:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Buy Order Error")
            return False
        # True일때 나오는거 확인해봐야함

        result = False
        if (response == str(200000)) or  (response == str(200)):
            result = True
        else : print("        API(" + str(sys._getframe().f_lineno) + ") ", response_before)


        return result

    def GetSellOrder(self, currency_string, coin_string, amount, price):
        path = "/api/v1/orders"
        kwargs = {'data': {"clientOid":"Django" + str(time.time()),"side" : "sell", "symbol": coin_string + "-" + currency_string, "type" : "limit", "price" : price, "size" : amount }}
        try :
            response_before =self._request('post', path,True, **kwargs)
            response = response_before['code'] #['success'] # true(성공값)
        except :
            try : print("        API(" + str(sys._getframe().f_lineno) + ") Get Sell Order Error / Message : ",response_before)
            except : print("        API(" + str(sys._getframe().f_lineno) + ") Get Sell Order Error")
            return False
        # True일때 나오는거 확인해봐야함
        result = False

        if (response == str(200000)) or  (response == str(200)):
            result = True
        else : print("        API(" + str(sys._getframe().f_lineno) + ") ", response_before)

        return result


    def GetWithdrawal(self, coin_string, amount, address):
        path = "/api/v1/withdrawals"

        if not self.GetTransfer(coin_string, amount, "trade","main") :
            print("        API(" + str(sys._getframe().f_lineno) + ") Get Withdrawal Error / Transfer Error")
            quit()

        kwargs = {'data': {"currency" : coin_string, "address" : address['address'], "amount" : amount }}
        try : kwargs['data']['memo'] = address['memo']
        except : kwargs['data']['address'] = address['address']

        try :
            response_before =self._request('post', path,True, **kwargs)
            response = response_before['code'] # ['success'] # true(성공값)
        except :
            try:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Withdrawal Error / Message : ",
                      response_before)
            except:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Withdrawal Error")

            return False

        result = False
        if response == str(200000) :
            result = True

        return result

    def CreateAccounts(self, coin_string, type):
        path = "/api/v1/accounts"
        kwargs = {'data': {"type" : type, "currency": coin_string}}
        try :
            response_before =self._request('post', path,True, **kwargs)
            response = response_before['data']['id']

        except:
            try:
                print("        API(" + str(sys._getframe().f_lineno) + ") Create Accounts Error / Message : ",
                      response_before)
            except:
                print("        API(" + str(sys._getframe().f_lineno) + ") Create Accounts Error")
                return {}



        return response

    def GetAccounts(self, coin_string):
        path = "/api/v1/accounts"
        kwargs = {'data': {"currency": coin_string}}
        try :
            response_before =self._request('get', path,True, **kwargs)
            response = response_before['data']
            # trade나 main 중 하나밖에 없으면 위에서 생성
        except :
            try:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Accounts Error / Message : ",
                      response_before)
            except:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Accounts Error")

            return {}

        result = {}
        for i in response :
            result[i['type']] = i['id']

        return result

    def GetTransfer(self, coin_string, amount,fromType,toType):
        path = "/api/v1/accounts/inner-transfer"
        accountInfo = self.GetAccounts(coin_string)
        kwargs = {'data': {"clientOid": "Django" + str(time.time()), "payAccountId": accountInfo[fromType], "recAccountId": accountInfo[toType], "amount": amount}}

        #
        #
        try :
            response_before =self._request('post', path,True, **kwargs)
            print(response_before )
            response = response_before['data']
            # trade나 main 중 하나밖에 없으면 위에서 생성
        except :
            try:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Transfer Error / Message : ",
                      response_before)
            except:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Transfer Error")

            return False

        return True


class GateAPI(BaseAPI):
    def __init__(self):
        self.name = "Gate"
        BaseAPI.__init__(self, GlobalVariable.keyPair[GlobalVariable.marketList[0]][0], GlobalVariable.keyPair[GlobalVariable.marketList[0]][1])
        self.BaseURL="https://data.gate.io"

    def _init_session(self):
        session = requests.session()
        return session

    def _request(self, method, path, **kwargs) :
        kwargs['timeout'] = 10
        kwargs['data'] = kwargs.get('data', {})
        kwargs['headers'] = kwargs.get('headers',{})
        uri = self.BaseURL + path
        nonce = self._getNonce()
        if method == 'post' :
            kwargs['data']["nonce"] = nonce
            kwargs['headers']['KEY'] = self.public_key
            kwargs['headers']['SIGN'] =self._generate_signature(kwargs['data'])

        if kwargs['data'] and method == 'get' :
            kwargs['params'] = kwargs['data']
            del(kwargs['data'])

        response = getattr(self.session, method)(uri, **kwargs)
        json = response.json()

        return json




    def _order_params_for_sig(self, data):

        strs = []
        for key in data :
            strs.append("{}={}".format(key, data[key]))
        return '&'.join(strs)
    def _generate_signature(self, data) :
        query_string = self._order_params_for_sig(data).encode('utf-8')
        m = hmac.new(self.private_key.encode('utf-8'), query_string, hashlib.sha512)
        return m.hexdigest()

    def GetTickers(self):
        path = "/api2/1/tickers"
        kwargs = {}
        result = {}
        try :
            result_response = self._request('get', path, **kwargs)
        except :
            try:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Tickers Error / Message : ",
                      result_response)
            except:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Tickers Error")
            return False

        for i in list(result_response.keys()) :
            if GlobalVariable.notTradeCoinList.count(i.split("_")[0].upper()) :
                continue
            if not list(result.keys()).count(i.split("_")[1].upper()) :
                result[i.split("_")[1].upper()] = [i.split("_")[0].upper()]
            else :
                result[i.split("_")[1].upper()].append(i.split("_")[0].upper())
        # print("Tickers ( Gate )")

        # V1_1 임시추가
        result2 = {}
        for key_result in result:
            for value_result in result[key_result]:
                if GlobalVariable.tradeCoinList[self.name].count(value_result):
                    try :
                        result2[key_result].append(value_result)
                    except :
                        result2[key_result] = [value_result]

        result = result2
        return result

    def GetOrderBook(self, currency_string, coin_string):
        path = "/api2/1/orderBook/" + coin_string + "_" + currency_string
        # while True :
        kwargs = {}
        result = {}
        wannabuy = {}
        wannasell = {}

        # print(currency_string)
        # print(coin_string)

        try :
            result_response = self._request('get', path, **kwargs)
            result_response["bids"]
            result_response["asks"]
            for i in result_response["bids"]:
                wannabuy[i[0]] = i[1]
            for j in result_response["asks"]:
                wannasell[j[0]] = j[1]
            result["wannabuy"] = wannabuy
            result["wannasell"] = wannasell

            # break
        except : return result

        return result


    def GetBalance(self):
        path = "/api2/1/private/balances"
        kwargs = {}

        try :
            response_before =self._request('post', path, **kwargs)

            response = response_before['available']

        except :
            try:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Balance Error / Message : ",
                      response_before)
            except:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Balance Error")
            quit()

        return response

    def GetDepositAddress(self, coin_string):
        path = "/api2/1/private/depositAddress"
        kwargs = {}
        kwargs["data"] = {"currency" : coin_string}

        try :
            response_before =self._request('post', path, **kwargs)
            response = response_before ['addr']

        except :
            try:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Deposit Address Error / Message : ",
                      response_before)
            except:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Deposit Address Error")
            return False

        result = {}
        if response.find(" ")>=0 :
            result['address'] =response.split(' ')[0]
            result['memo'] = response.split(' ')[1]
        else :
            result['address'] = response
        response = result

        return response

    def GetBuyOrder(self, currency_string, coin_string, amount, price):
        path = "/api2/1/private/buy"
        kwargs = {}
        kwargs["data"] = {"currencyPair": coin_string + "_" + currency_string, "rate" : price, "amount" : amount}
        try :
            response_before = self._request('post', path, **kwargs)
            response = response_before['result'] # 참값 : 'true'

        except :
            try:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Buy Order / Message : ",
                      response_before)
            except:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Buy Order Error")
            return False

        result = False
        if str(response).upper() == "TRUE": result = True
        else : print("        API(" + str(sys._getframe().f_lineno) + ") ", response_before)


        return result

    def GetSellOrder(self, currency_string, coin_string, amount, price):
        path = "/api2/1/private/sell"
        kwargs = {}
        kwargs["data"] = {"currencyPair": coin_string + "_" + currency_string, "rate": price, "amount": amount}
        try :
            response_before =self._request('post', path, **kwargs)
            response = response_before ['result'] # 참값 : 'true'

        except :
            try:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Sell Order Error / Message : ",
                      response_before)
            except:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Sell Order Error")

        result = False
        if str(response).upper() == "TRUE":
            result = True
        else: print("        API(" + str(sys._getframe().f_lineno) + ") ", response_before)

        return result

    def GetOpenOrderCheck(self, currency_string, coin_string):
        path = "/api2/1/private/openOrders"
        kwargs = {}
        result = {}
        try :
            response_before = self._request('post', path, **kwargs)
            print("response_before", response_before )
            response = response_before['orders'] # 참값 : 'true'

        except :
            try:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Open Order Check Error / Message : ",
                      response_before)
            except:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Open Order Check Error")

        for i in response:
            try:
                result[float(i['rate'])] = float(i['amount'])
            except:
                result = {}
        return result

    def GetCancelOrders(self, currency_string, coin_string):
        path = "/api2/1/private/cancelAllOrders"
        kwargs = {}
        kwargs["data"] = {"type": -1 , "currencyPair": coin_string + "_" + currency_string}
        try :
            response_before =self._request('post', path, **kwargs)
            response = response_before['result']  # 참값 : 'true'
        except :
            try:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Cancel Order Error / Message : ",
                      response_before)
            except:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Cancel Order Error")
            return False

        result = False
        if str(response).upper() == "TRUE":
            result = True
        else:
            print(response)
        return result

    def GetWithdrawal(self, coin_string, amount, address):
        path = "/api2/1/private/withdraw"
        kwargs = {}
        kwargs["data"] = {"currency" : coin_string, "amount" : amount, "address" : address['address']}

        try :
            kwargs['data']['address'] = address['address'] + " " + address['memo']  # address에 memo 포함시 변경
        except : kwargs['data']['address'] = address['address']

        try :
            response_before =self._request('post', path, **kwargs)
            print(response_before)
            response = response_before['result']  # 참값 : 'true'
        except :
            try:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Withdrawal Error / Message : ",
                      response_before)
            except:
                print("        API(" + str(sys._getframe().f_lineno) + ") Get Withdrawal Error")
            return False

        result = False
        if str(response).upper() == "TRUE":
            result = True
        else:
            print(response)
        return result

class BithumbAPI(BaseAPI):
    def __init__(self):
        self.name = "Bithumb"
        BaseAPI.__init__(self, GlobalVariable.keyPair[GlobalVariable.marketList[2]][0], GlobalVariable.keyPair[GlobalVariable.marketList[2]][1])
        self.BaseURL="https://api.bithumb.com"
        self.orderList = []


    def _init_session(self):
        session = requests.session()
        return session


    def _request(self, method, path, **kwargs) :
        time.sleep(0.1) # 거래소 1초에 http통신 제한
        kwargs['timeout'] = 10
        kwargs['data'] = kwargs.get('data', {})
        kwargs['headers'] = kwargs.get('headers',{})
        uri = self.BaseURL + path
        self.path = path
        self.nonce = self._getNonce()

        if method == 'post' :
            kwargs['headers']['Api-Key'] = self.public_key
            kwargs['headers']['Api-Sign'] = self._generate_signature(kwargs['data'])
            kwargs['headers']['Api-Nonce'] = self.nonce



        if kwargs['data'] and method == 'get' :
            kwargs['params'] = kwargs['data']
            del(kwargs['data'])

        # print(kwargs)
        response = getattr(self.session, method)(uri, **kwargs)
        json = response.json()

        return json
    def _order_params_for_sig(self, data):

        strs = []
        for key in data :
            strs.append("{}={}".format(key, data[key]))
        return '&'.join(strs)
    def _generate_signature(self, data) :
        str_data = urllib.parse.urlencode(data)

        utf8_data = (self.path + chr(0) + str_data + chr(0) + self.nonce).encode('utf-8')

        utf8_key = self.private_key.encode('utf-8')

        h = hmac.new(bytes(utf8_key), utf8_data, hashlib.sha512)

        hex_output = h.hexdigest()

        utf8_hex_output = hex_output.encode('utf-8')

        api_sign = base64.b64encode(utf8_hex_output)

        utf8_api_sign = api_sign.decode('utf-8')

        return utf8_api_sign

    def GetTickers(self):
        path = "/public/ticker/all"
        kwargs = {}
        result = {}


        while True :
            try :
                response_before = self._request('get', path, **kwargs)
                result_response = response_before["data"]
                break
            except :

                print("API/540")
                try : print(response_before)
                except : time.sleep(10)
        coinList = []
        for i in list(result_response.keys()) :
            coinList.append(str(i))

        coinList.remove("date")
        result["KRW"] = coinList

        # print("Tickers ( Bithumb )")
        return result


    def GetOrderBook(self, currency_string, coin_string):
        path = "/public/orderbook/" + coin_string

        kwargs = {}
        result = {}
        wannasell = {}
        wannabuy = {}
        if currency_string == coin_string :
            result["wannabuy"] = wannabuy
            result["wannasell"] = wannasell
            return result
        # while True :

        try :
            response_before =self._request('get', path, **kwargs)
            response = response_before['data']
            for i in response["bids"]:
                wannabuy[float(i['price'])] = float(i['quantity'])
            for i in response["asks"]:
                wannasell[float(i['price'])] = float(i['quantity'])

            result["wannabuy"] = wannabuy
            result["wannasell"] = wannasell

            # break
        except :
            print("Getting OrderBook Again")


        # print("OrderBook ( Bithumb : " + currency_string + " - " + coin_string + " )")
        return result


    def GetBalance(self):
        path = "/info/balance"
        kwargs = {"data" : {
            "currency" : "all"
        }}
        result = {}
        while True :
            try :
                response_before =self._request('post', path, ** kwargs)
                response = response_before ['data']
                # print(response_before)
                break
            except :
                print("API 613")
                try : print(response_before)
                except : time.sleep(10)


        for i in response :
            if i.split("_")[0] == "available" :
                result[i.split("_")[1].upper()] = response[i]
        return result

    def GetDepositAddress(self, coin_string):
        path = "/info/wallet_address"
        kwargs = {"data" : {
            "currency" : coin_string
        }
        }
        while True :
            try :
                response_before =self._request('post', path, **kwargs)
                response = response_before['data']['wallet_address']
                break
            except :
                print("API 182")
                try : print(response_before)
                except : time.sleep(10)
        return response

    def GetOpenOrderCheck(self, currency_string, coin_string):
        result = True
        for i in self.orderList :
            path = "/info/orders"

            kwargs = {"data": {
                "order_id" : i,
                "type" : self.orderType,
                "currency" : coin_string

            }
            }

            while True :
                try :
                    response_before =self._request('post', path, **kwargs)
                    # print(response_before)
                    response = response_before['data']
                    break
                except :
                    print("API 713")
                    try:
                        print(response_before)
                    except:
                        print("waiting..")
                        time.sleep(10)
            if response[0]["status"] == "placed" :
                result = result and False
            else :
                result = result and True
                self.orderList = []
                self.orderType = ""

        return result

    def GetCancelOrders(self, currency_string, coin_string):
        path = "/trade/cancel"
        result = True
        if len(self.orderList) == 0 :
            print("No orderList")
            exit()
        for i in self.orderList :
            kwargs = {"data": {
                "type": self.orderType,
                "order_id": i,
                "currency": coin_string
            }
            }
            while True :
                try :
                    response_before = self._request( 'post', path, **kwargs)
                    print(response_before)
                    response = response_before["status"]
                    break
                except :
                    print("API 749")
                    try:
                        print(response_before)
                    except:
                        time.sleep(10)
            if response == "0000" :
                result = result and True
                self.orderList = []
                self.orderType = ""
            else :
                result = result and False

        return result
    #
    def GetBuyOrder(self, currency_string, coin_string, amount, price):
        path = "/trade/place"
        kwargs = {"data": {
            "order_currency": coin_string,
            "Payment_currency" : currency_string,
            "units" : amount,
            "price" : price,
            "type" : "bid"
        }}
        while True :
            try :
                response_before =self._request('post', path, **kwargs)
                print(response_before)
                response = response_before['status']
                break
            except :
                print("API 763")
                try : print(response_before)
                except : time.sleep(10)


        # result = False
        if str(response) == "0000" :
            result = True
            self.orderList.append(response_before["order_id"])
            self.orderType = "bid"
        else : result = False
        return result
    #
    def GetSellOrder(self, currency_string, coin_string, amount, price):
        path = "/trade/place"
        kwargs = {"data": {
            "order_currency": coin_string,
            "Payment_currency" : currency_string,
            "units" : amount,
            "price" : price,
            "type" : "ask"
        }}
        while True :
            try :
                response_before = self._request('post', path, **kwargs)
                response = response_before['status']
                break
            except :
                print("API 247")
                try : print(response_before)
                except : time.sleep(10)
        if str(response) == "0000" :
            result = True
            self.orderList.append(response_before["order_id"])
            self.orderType = "ask"
        else : result = False
        return result
    #
    #
    def GetWithdrawal(self, coin_string, amount, address):
        path = "/trade/btc_withdrawal"
        kwargs = {"data": {
            "units": amount,
            "address": address,
            "currency" : coin_string
        }}
        while True :
            try :
                response_before = self._request('post', path, **kwargs)
                # print(response_before)
                response = response_before['status']

                break
            except :
                print("API 804")
                try:
                    print(response_before)
                except:
                    time.sleep(10)

        result = False
        if str(response) == "0000" :
            result = True
        else : print(response)
        return result

class CoinnestAPI(BaseAPI):
    def __init__(self):
        self.name = "Coinnest"
        BaseAPI.__init__(self, GlobalVariable.keyPair[GlobalVariable.marketList[3]][0], GlobalVariable.keyPair[GlobalVariable.marketList[3]][1])
        self.BaseURL="https://api.coinnest.co.kr/api"

    def _init_session(self):
        session = requests.session()
        return session

    def _request(self, method, path, **kwargs) :
        kwargs['timeout'] = 10
        kwargs['data'] = kwargs.get('data', {})
        kwargs['headers'] = kwargs.get('headers',{})
        uri = self.BaseURL + path
        nonce = self._getNonce()
        if method == 'post' :
            kwargs['data']["nonce"] = nonce
            kwargs['headers']['KEY'] = self.public_key
            kwargs['headers']['SIGN'] =self._generate_signature(kwargs['data'])

        if kwargs['data'] and method == 'get' :
            kwargs['params'] = kwargs['data']
            del(kwargs['data'])

        response = getattr(self.session, method)(uri, **kwargs)
        json = response.json()

        return json




    def _order_params_for_sig(self, data):

        strs = []
        for key in data :
            strs.append("{}={}".format(key, data[key]))
        return '&'.join(strs)

    def _generate_signature(self, data) :
        query_string = self._order_params_for_sig(data).encode('utf-8')
        m = hmac.new(self.private_key.encode('utf-8'), query_string, hashlib.sha512)
        return m.hexdigest()

    def GetTickers(self):
        path = "/pub/tickerall"
        kwargs = {}
        result = {}

        while True :
            try :
                response = self._request('get', path, **kwargs)
                break
            except :

                print("API/950")
                try : print(response)
                except : time.sleep(10)
        coinList = []
        for i in list(response.keys()) :
            coinList.append(i.split("_")[1])

        result["KRW"] = coinList
        #
        # print("Tickers ( Coinnest )")

        return result


    def GetOrderBook(self, currency_string, coin_string):
        path = "/pub/depth?coin=" + coin_string.lower()


        kwargs = {}
        result = {}
        wannasell = {}
        wannabuy = {}
        # while True :
        try :
            response=self._request('get', path, **kwargs)

            for i in response["bids"]:
                wannabuy[float(i[0])] = float(i[1])
            for i in response["asks"]:
                wannasell[float(i[0])] = float(i[1])

            result["wannabuy"] = wannabuy
            result["wannasell"] = wannasell

            # break
        except :
            print("Getting OrderBook Again")



        # print("OrderBook ( Bithumb : " + currency_string + " - " + coin_string + " )")
        return result

class PoloniexAPI(BaseAPI):
    def __init__(self):
        self.name = "Poloniex"

        BaseAPI.__init__(self, GlobalVariable.keyPair[GlobalVariable.marketList[3]][0], GlobalVariable.keyPair[GlobalVariable.marketList[3]][1])
        self.BaseURL="https://poloniex.com/"

    def _init_session(self):
        session = requests.session()
        return session

    def _getNonce(self):
        nonce = int(time.time())
        return str(nonce)

    def _request(self, method, path, **kwargs) :
        kwargs['timeout'] = 10
        kwargs['data'] = kwargs.get('data', {})
        kwargs['headers'] = kwargs.get('headers',{})
        if kwargs['data'] and method == 'get':
            uri = self.BaseURL + path + "?" + self._order_params_for_sig(kwargs['data'])
        else : uri = self.BaseURL + path
        nonce = self._getNonce()
        kwargs['headers']['KC-API-KEY'] = self.public_key
        kwargs['headers']['KC-API-NONCE'] = nonce
        kwargs['headers']['KC-API-SIGNATURE'] =self._generate_signature(path, kwargs['data'], nonce)
        if kwargs['data'] and method == 'get' :
            kwargs['params'] = kwargs['data']
            del(kwargs['data'])


        response = getattr(self.session, method)(uri, **kwargs)
        json = response.json()

        return json

    def _generate_signature(self, path, data, nonce) :
        query_string = self._order_params_for_sig(data)
        sig_str = ("{}/{}/{}".format(path, nonce, query_string)).encode('utf-8')
        m = hmac.new(self.private_key.encode('utf-8'), base64.b64encode(sig_str), hashlib.sha256)
        return m.hexdigest()


    def _order_params_for_sig(self, data):
        strs = []
        for key in sorted(data) :
            strs.append("{}={}".format(key, data[key]))
        return '&'.join(strs)

    def GetTickers(self):
        path = "public?command=returnTicker"
        kwargs = {}
        result = {}
        while True :
            try :
                response = self._request('get', path, **kwargs)
                break
            except :
                print("API/1243")
                try : print(response)
                except : time.sleep(10)


        # print(response)
        for i in response.keys() :
            if not list(result.keys()).count(i.split("_")[0]) :
                if not i.split("_")[0] == i.split("_")[1] :
                    result[i.split("_")[0]] = [i.split("_")[1]]
            else :
                if not i.split("_")[0] == i.split("_")[1] :
                    result[i.split("_")[0]].append(i.split("_")[1])
                # print("Tickers ( Kucoin )")



        # V1_1 임시추가 // Coinlist에 있는것만 들어가게 하는것
        result2 = {}
        for key_result in result:
            for value_result in result[key_result]:
                if GlobalVariable.tradeCoinList[self.name].count(value_result):
                    try :
                        result2[key_result].append(value_result)
                    except :
                        result2[key_result] = [value_result]

        result = result2
        return result


    def GetOrderBook(self, currency_string, coin_string):

        path = "public?command=returnOrderBook&currencyPair=" + currency_string + "_" + coin_string

        kwargs = {}
        result = {}
        wannasell = {}
        wannabuy = {}
        if currency_string == coin_string :
            result["wannabuy"] = wannabuy
            result["wannasell"] = wannasell
            return result
        # while True :
        try :
            response = self._request('get', path, **kwargs)

            if response["bids"]:
                for i in response["bids"]:
                    wannabuy[float(i[0])] = i[1]
            # else : print("API/129) " + str(response))
            if response["asks"]:
                for j in response["asks"]:
                    wannasell[float(j[0])] = j[1]
            # else: print("API/133) " + str(response))
            result["wannabuy"] = wannabuy
            result["wannasell"] = wannasell

            # break
        except :
            print("Getting OrderBook Again" + currency_string + "-" + coin_string)
                # try : print(response)
                # except : time.sleep(10)


        # print("OrderBook ( Kucoin : " + currency_string + " - " + coin_string + " )")
        return result



class GopaxAPI(BaseAPI):
    def __init__(self):
        self.name = "Gopax"
        BaseAPI.__init__(self, GlobalVariable.keyPair[GlobalVariable.marketList[4]][0], GlobalVariable.keyPair[GlobalVariable.marketList[4]][1])
        self.BaseURL="https://api.gopax.co.kr/"

    def _init_session(self):
        session = requests.session()
        return session

    def _request(self, method, path, **kwargs) :
        kwargs['timeout'] = 10
        kwargs['data'] = kwargs.get('data', {})
        kwargs['headers'] = kwargs.get('headers',{})
        uri = self.BaseURL + path
        nonce = self._getNonce()
        if method == 'post' :
            kwargs['data']["nonce"] = nonce
            kwargs['headers']['KEY'] = self.public_key
            kwargs['headers']['SIGN'] =self._generate_signature(kwargs['data'])

        if kwargs['data'] and method == 'get' :
            kwargs['params'] = kwargs['data']
            del(kwargs['data'])

        response = getattr(self.session, method)(uri, **kwargs)
        json = response.json()

        return json




    def _order_params_for_sig(self, data):

        strs = []
        for key in data :
            strs.append("{}={}".format(key, data[key]))
        return '&'.join(strs)

    def _generate_signature(self, data) :
        query_string = self._order_params_for_sig(data).encode('utf-8')
        m = hmac.new(self.private_key.encode('utf-8'), query_string, hashlib.sha512)
        return m.hexdigest()

    def GetTickers(self):
        path = "assets"
        kwargs = {}
        result = {}

        while True :
            try :
                response = self._request('get', path, **kwargs)
                break
            except :

                print("API/950")
                try : print(response)
                except : time.sleep(10)
        coinList = []
        for i in response :
            if i["id"] == "KRW" : continue
            coinList.append(i["id"])

        result["KRW"] = coinList
        #
        # print("Tickers ( Coinnest )")

        return result


    def GetOrderBook(self, currency_string, coin_string):
        path = "trading-pairs/" + coin_string + "-KRW/book"


        kwargs = {}
        result = {}
        wannasell = {}
        wannabuy = {}
        # while True :
        try :
            response=self._request('get', path, **kwargs)
            for i in response["bid"]:
                wannabuy[i[1]] = i[2]
            for i in response["ask"]:
                wannasell[i[1]] = i[2]

            result["wannabuy"] = wannabuy
            result["wannasell"] = wannasell

            # break
        except :
            print("Getting OrderBook Again")

                # try :
                #     print(coin_string)
                # except : time.sleep(10)

        # print(response)
        # print(response["bid"])

        # print("OrderBook ( Bithumb : " + currency_string + " - " + coin_string + " )")
        return result



class BinanceAPI(BaseAPI):
    def __init__(self):
        self.name = "Binance"

        BaseAPI.__init__(self, GlobalVariable.keyPair[GlobalVariable.marketList[5]][0], GlobalVariable.keyPair[GlobalVariable.marketList[5]][1])
        self.BaseURL="https://api.binance.com/"

    def _init_session(self):
        session = requests.session()
        return session

    def _getNonce(self):
        nonce = int(time.time())
        return str(nonce)

    def _request(self, method, path, **kwargs) :
        kwargs['timeout'] = 10
        kwargs['data'] = kwargs.get('data', {})
        kwargs['headers'] = kwargs.get('headers',{})
        if kwargs['data'] and method == 'get':
            uri = self.BaseURL + path + "?" + self._order_params_for_sig(kwargs['data'])
        else : uri = self.BaseURL + path
        nonce = self._getNonce()
        kwargs['headers']['KC-API-KEY'] = self.public_key
        kwargs['headers']['KC-API-NONCE'] = nonce
        kwargs['headers']['KC-API-SIGNATURE'] =self._generate_signature(path, kwargs['data'], nonce)
        if kwargs['data'] and method == 'get' :
            kwargs['params'] = kwargs['data']
            del(kwargs['data'])


        response = getattr(self.session, method)(uri, **kwargs)
        json = response.json()

        return json

    def _generate_signature(self, path, data, nonce) :
        query_string = self._order_params_for_sig(data)
        sig_str = ("{}/{}/{}".format(path, nonce, query_string)).encode('utf-8')
        m = hmac.new(self.private_key.encode('utf-8'), base64.b64encode(sig_str), hashlib.sha256)
        return m.hexdigest()


    def _order_params_for_sig(self, data):
        strs = []
        for key in sorted(data) :
            strs.append("{}={}".format(key, data[key]))
        return '&'.join(strs)

    def GetTickers(self):
        path = "api/v3/ticker/price"
        kwargs = {}
        result = {"BTC" : [], "ETH" : [], "USDT" : [], "BNB" : []}
        while True :
            try :
                response = self._request('get', path, **kwargs)
                break
            except :
                print("API/1243")
                try : print(response)
                except : time.sleep(10)


        # print(response)
        for i in response :
            if i["symbol"][len(i["symbol"])-3:] == "BTC" :
                result["BTC"].append(i["symbol"][:len(i["symbol"])-3])
            elif i["symbol"][len(i["symbol"])-3:] == "ETH" :
                result["ETH"].append(i["symbol"][:len(i["symbol"]) - 3])
            elif i["symbol"][len(i["symbol"]) - 3:] == "BNB":
                result["BNB"].append(i["symbol"][:len(i["symbol"]) - 3])
            elif i["symbol"][len(i["symbol"]) - 4:] == "USDT":
                result["USDT"].append(i["symbol"][:len(i["symbol"]) - 4])



        # V1_1 임시추가 // Coinlist에 있는것만 들어가게 하는것
        result2 = {}
        for key_result in result:
            for value_result in result[key_result]:
                if GlobalVariable.tradeCoinList[self.name].count(value_result):
                    try :
                        result2[key_result].append(value_result)
                    except :
                        result2[key_result] = [value_result]

        result = result2
        return result


    def GetOrderBook(self, currency_string, coin_string):

        path = "/api/v1/depth?symbol=" + coin_string + currency_string

        kwargs = {}
        result = {}
        wannasell = {}
        wannabuy = {}
        if currency_string == coin_string :
            result["wannabuy"] = wannabuy
            result["wannasell"] = wannasell
            return result
        # while True :
        try :
            response = self._request('get', path, **kwargs)

            if response["bids"]:
                for i in response["bids"]:
                    wannabuy[float(i[0])] = float(i[1])
            # else : print("API/129) " + str(response))
            if response["asks"]:
                for j in response["asks"]:
                    wannasell[float(j[0])] = float(j[1])
            # else: print("API/133) " + str(response))
            result["wannabuy"] = wannabuy
            result["wannasell"] = wannasell

            # break
        except :
            print("Getting OrderBook Again" + currency_string + "-" + coin_string)
                # try : print(response)
                # except : time.sleep(10)


        # print("OrderBook ( Kucoin : " + currency_string + " - " + coin_string + " )")
        return result


# -*- coding: utf-8 -*
import requests, time, hmac, hashlib
from app.authorization import recv_window,api_secret,api_key

try:
    from urllib import urlencode
# python3
except ImportError:
    from urllib.parse import urlencode

class OkexAPI(object):
    BASE_URL_V3 = "https://aws.okex.com/api/spot/v3"

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def get_ticker_price(self,market):
        path = "%s/instruments/%s/ticker" % (self.BASE_URL_V3, market)
        res =  self._get_no_sign(path)
        time.sleep(2)
        return float(res['best_ask'])

    def buy_limit(self, market, quantity, rate, client_oid):
        path = "%s/orders" % self.BASE_URL_V3
        params = self._order(market, quantity, "buy", client_oid, rate)
        return self._post(path, params)

    def sell_limit(self, market, quantity, rate, client_oid):
        path = "%s/orders" % self.BASE_URL_V3
        params = self._order(market, quantity, "sell", client_oid, rate)
        return self._post(path, params)

    ### ----私有函数---- ###
    def _order(self, market, quantity, side, client_oid, now_price, price=None):
        '''
        :param market:币种类型。如：BTCUSDT、ETHUSDT
        :param quantity: 购买量
        :param now_price: 当前价格，用于计算买入时的计价货币数量
        :param side: 订单方向，买还是卖
        :param price: 价格
        :param client_oid: 唯一id
        :return:
        '''
        params = {}

        if price is not None:
            params["type"] = "limit"
            params["price"] = self._format(price)
        else:
            params["type"] = "market"
            if side == "buy":
                params["notional"] = '%.2f' % (quantity * now_price)

        params["instrument_id"] = market
        params["client_oid"] = client_oid
        params["side"] = side
        params["quantity"] = '%.8f' % quantity

        return params

    def _get_no_sign(self, path, params={}):
        query = urlencode(params)
        url = "%s?%s" % (path, query)
        return requests.get(url, timeout=180, verify=True).json()

    def _sign(self, params={}):
        data = params.copy()

        ts = int(1000 * time.time())
        data.update({"timestamp": ts})
        h = urlencode(data)
        b = bytearray()
        b.extend(self.secret.encode())
        signature = hmac.new(b, msg=h.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
        data.update({"signature": signature})
        return data

    def _post(self, path, params={}):
        params.update({"recvWindow": recv_window})
        query = urlencode(self._sign(params))
        url = "%s" % (path)
        header = {"X-MBX-APIKEY": self.key}
        return requests.post(url, headers=header, data=query, \
            timeout=180, verify=True).json()

    def _format(self, price):
        return "{:.8f}".format(price)

if __name__ == "__main__":
    instance = OkexAPI(api_key,api_secret)
    # print(instance.buy_limit("EOSUSDT",5,2))
    print(instance.get_ticker_price("OKB-USDT"))
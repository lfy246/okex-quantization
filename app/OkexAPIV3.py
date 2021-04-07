# -*- coding: utf-8 -*
import requests, time, hmac, hashlib
from app.authorization import okex_api_key, okex_api_secret, okex_passphrase
from app.okex import spot_api as spot

try:
    from urllib import urlencode
# python3
except ImportError:
    from urllib.parse import urlencode

class OkexAPIV3(object):

    def __init__(self, key, secret, okex_passphrase):
        self.spotAPI = spot.SpotAPI(key, secret, okex_passphrase)

    def get_ticker_price(self,market):
        res = self.spotAPI.get_specific_ticker(market)
        best_ask = res['best_ask']
        print(best_ask)
        time.sleep(2)
        return float(best_ask)

    def buy_limit(self, market, quantity, rate, client_oid, now_price):
        return self._task_order(market, quantity, "buy", client_oid, now_price, rate)

    def sell_limit(self, market, quantity, rate, client_oid, now_price):
        return self._task_order(market, quantity, "sell", client_oid, now_price, rate)

    ### ----私有函数---- ###

    def _task_order(self,market, quantity, side, client_oid, now_price, price=None):
        """
        :param market:币种类型。如：BTCUSDT、ETHUSDT
        :param quantity: 购买量
        :param now_price: 当前价格，用于计算买入时的计价货币数量
        :param side: 订单方向，买还是卖
        :param price: 价格
        :param client_oid: 唯一id
        :return:
        """
        notional = ''
        if price is not None:
            type = "limit"
            price = self._format(price)
        else:
            type = "market"
            if side == "buy":
                notional = '%.2f' % (quantity * now_price)
        side = side
        size = '%.8f' % quantity
        result = self.spotAPI.take_order(instrument_id=market, side=side,
                                         client_oid=client_oid , type=type,
                                         size=size, price=price,
                                         order_type='0', notional=notional)
        print(result)
        return result

    def _format(self, price):
        return "{:.8f}".format(price)

if __name__ == "__main__":
    instance = OkexAPI(api_key,api_secret)
    # print(instance.buy_limit("EOSUSDT",5,2))
    print(instance.get_ticker_price("OKB-USDT"))
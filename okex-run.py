# -*- coding: utf-8 -*-
from app.OkexAPIV3 import OkexAPIV3
from app.authorization import okex_api_key, okex_api_secret, okex_passphrase
from data.runBetData import RunBetData
from app.dingding import Message
import time

okex = OkexAPIV3(okex_api_key, okex_api_secret, okex_passphrase)
runbet = RunBetData()

class Run_Main():

    def __init__(self):
        self.coinType = runbet.get_cointype()  # 交易币种
        self.message = Message()
        pass


    def loop_run(self):
        while True:
            cur_market_price = 0
            try:
                cur_market_price = okex.get_ticker_price(runbet.get_cointype())  # 当前交易对市价
            except Exception as e:
                print("获取交易价失败：{}".format(e))
                time.sleep(5)
                continue
            grid_buy_price = runbet.get_buy_price()  # 当前网格买入价格
            grid_sell_price = runbet.get_sell_price() # 当前网格卖出价格
            quantity = runbet.get_quantity()   # 买入量
            step = runbet.get_step() # 当前步数
            result = ''
            client_oid = "okex%s" % int(time.time())
            if grid_buy_price >= cur_market_price:   # 是否满足买入价
                try:
                    print("满足条件，开始买入{}:{}".format(self.coinType, grid_buy_price))
                    result = okex.buy_limit(self.coinType, quantity, grid_buy_price, client_oid, cur_market_price)
                    print("买入结果：{}".format(result))
                    if result['order_id'] != '-1':
                        buy_info = "报警：币种为：{cointype}。买单价为：{price}。买单量为：{num}".format(cointype=self.coinType, price=grid_buy_price,
                                                                                      num=quantity)
                        self.message.dingding_warn(buy_info)
                        runbet.modify_price(grid_buy_price, step + 1)  # 修改data.json中价格、当前步数
                        time.sleep(60 * 2)  # 挂单后，停止运行1分钟
                except BaseException as e:
                    print("买入出错：{}",e)
                    error_info = "报警：币种为：{cointype},买单失败.api返回内容为:{reject},error:{error}".format(cointype=self.coinType, reject=result, error = e)
                    self.message.dingding_warn(error_info + str(result))
                    pass

            elif grid_sell_price < cur_market_price:  # 是否满足卖出价
                if step==0: # setp=0 防止踏空，跟随价格上涨
                    runbet.modify_price(grid_sell_price,step)
                else:
                    try:
                        print("满足条件，开始出售{}:{}".format(self.coinType, grid_sell_price))
                        result = okex.sell_limit(self.coinType, quantity, grid_sell_price, client_oid, cur_market_price)
                        if result['order_id'] != '-1':
                            buy_info = "报警：币种为：{cointype}。卖单价为：{price}。卖单量为：{num}".format(cointype=self.coinType, price=grid_sell_price,
                                                                                          num=quantity)
                            self.message.dingding_warn(buy_info)
                            runbet.modify_price(grid_sell_price, step - 1)
                            time.sleep(60 * 2)  # 挂单后，停止运行1分钟
                        else:
                            time.sleep(60 * 2)  # 挂单后，停止运行1分钟
                    except BaseException as e:
                        print("卖单：{}", e)
                        error_info = "报警：币种为：{cointype},卖单失败.api返回内容为:{reject}，错误信息：{error}".format(cointype=self.coinType,
                                                                                       reject=result,error = e)
                        self.message.dingding_warn(error_info + str(result))
                        pass

            else:
                print("当前市价：{market_price}。未能满足交易,继续运行".format(market_price = cur_market_price))


if __name__ == "__main__":
    instance = Run_Main()
    try:
        instance.loop_run()
    except Exception as e:
        print(e)
        error_info = "报警：币种{coin},服务停止,原因：{message}".format(coin=instance.coinType, message = e)
        instance.message.dingding_warn(error_info)

# 调试看报错运行下面，正式运行用上面
# if __name__ == "__main__":
    # instance = Run_Main()
    # instance.loop_run()

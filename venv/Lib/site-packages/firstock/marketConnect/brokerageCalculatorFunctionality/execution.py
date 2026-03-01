from firstock.marketConnect.brokerageCalculatorFunctionality.functions import *


class FirstockBrokerageCalculator:
    def __init__(
        self,
        userId,
        exchange,
        tradingSymbol,
        transactionType,
        product,
        quantity,
        price,
        strike_price,
        inst_name,
        lot_size
    ):
        self.brokerageCalculator = ApiRequests()
        self.userId = userId
        self.exchange = exchange
        self.tradingSymbol = tradingSymbol
        self.transactionType = transactionType
        self.product = product
        self.quantity = quantity
        self.price = price
        self.strike_price = strike_price
        self.inst_name = inst_name
        self.lot_size = lot_size

    def firstockBrokerageCalculator(self):
        result = self.brokerageCalculator.firstockBrokerageCalculator(
            self.userId,
            self.exchange,
            self.tradingSymbol,
            self.transactionType,
            self.product,
            self.quantity,
            self.price,
            self.strike_price,
            self.inst_name,
            self.lot_size
        )
        return result

from firstock.marketConnect.getExpiryFunctionality.functions import *


class expiryFirstock:
    def __init__(self, userId, exchange, tradingSymbol):
        self.firstockExpiry = ApiRequests()
        self.userId = userId
        self.exchange = exchange
        self.tradingSymbol = tradingSymbol

    def expiryFirstock(self):
        result = self.firstockExpiry.expiryFirstock(
            userId=self.userId,
            exchange=self.exchange,
            tradingSymbol=self.tradingSymbol
        )
        return result


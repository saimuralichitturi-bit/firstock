from firstock.marketConnect.getSecurityInfoFunctionality.functions import *


class FirstockGetSecurityInfo:
    def __init__(self, exchange, tradingSymbol, userId):
        self.getSecurityInfo = ApiRequests()
        self.exchange = exchange
        self.tradingSymbol = tradingSymbol
        self.userId = userId

    def firstockGetSecurityInfo(self):
        result = self.getSecurityInfo.firstockGetSecurityInfo(self.exchange, self.tradingSymbol, self.userId)
        return result

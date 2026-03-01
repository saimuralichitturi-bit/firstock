from firstock.marketConnect.getQuotesFunctionality.functions import *


class FirstockGetQuotes:
    def __init__(self, exchange, tradingSymbol, userId):
        self.getQuotes = ApiRequests()
        self.userId = userId
        self.exchange = exchange
        self.tradingSymbol = tradingSymbol

    def firstockGetQuotes(self):
        result = self.getQuotes.firstockGetQuotes(self.exchange, self.tradingSymbol, self.userId)
        return result

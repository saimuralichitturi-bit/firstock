from firstock.marketConnect.getOptionChainFunctionality.functions import *


class FirstockGetOptionChain:
    def __init__(self, symbol, exch, strprc, cnt, userId,expiry):
        self.getOptionChain = ApiRequests()
        self.userId = userId
        self.symbol = symbol
        self.exch = exch
        self.strprc = strprc
        self.cnt = cnt
        self.expiry =expiry

    def firstockGetOptionChain(self):
        result = self.getOptionChain.firstockGetOptionChain(self.symbol, self.exch, self.strprc, self.cnt, self.userId, self.expiry)
        return result

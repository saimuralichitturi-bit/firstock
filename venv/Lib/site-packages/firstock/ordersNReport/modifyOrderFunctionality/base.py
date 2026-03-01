from abc import ABC, abstractmethod


class FirstockAPI(ABC):
    @abstractmethod
    def firstockModifyOrder(self, qty, product, mkt_protection, orderNumber, trgprc, prc, tradingSymbol, priceType, userId):
        """
        :return:
        """
        pass

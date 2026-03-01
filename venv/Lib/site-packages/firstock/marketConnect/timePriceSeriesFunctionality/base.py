from abc import ABC, abstractmethod


class FirstockAPI(ABC):
    @abstractmethod
    def firstockTimePriceSeries(self, exch, tradingSymbol, st, et, intrv, userId):
        """
        :return:
        """
        pass


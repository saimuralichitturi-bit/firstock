from abc import ABC, abstractmethod


class FirstockAPI(ABC):
    @abstractmethod
    def expiryFirstock(self, userId, exchange, tradingSymbol):
        """
        Abstract method to fetch quote details for a trading symbol
        """
        pass

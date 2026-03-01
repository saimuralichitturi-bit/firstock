from abc import ABC, abstractmethod

class FirstockAPI(ABC):
    @abstractmethod
    def firstockBrokerageCalculator(self, userId, exchange, tradingSymbol, transactionType, product, quantity, price, strike_price, inst_name, lot_size):
        """
        Abstract method to be implemented for Brokerage Calculator API
        """
        pass


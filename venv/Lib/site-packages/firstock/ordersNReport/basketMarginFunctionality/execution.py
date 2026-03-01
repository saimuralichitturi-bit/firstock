from firstock.ordersNReport.basketMarginFunctionality.functions import *

class FirstockBasketMargin:
    def __init__(self, userId, exchange, transactionType, product,
                 tradingSymbol, quantity, priceType, price, BasketList_Params):
        self.BasketMargin = ApiRequests()
        self.userId = userId
        self.exchange = exchange
        self.transactionType = transactionType
        self.product = product
        self.tradingSymbol = tradingSymbol
        self.quantity = quantity
        self.priceType = priceType
        self.price = price
        self.BasketList_Params = BasketList_Params

    def firstockBasketMargin(self):
        return self.BasketMargin.firstockBasketMargin(
            userId=self.userId,
            exchange=self.exchange,
            transactionType=self.transactionType,
            product=self.product,
            tradingSymbol=self.tradingSymbol,
            quantity=self.quantity,
            priceType=self.priceType,
            price=self.price,
            BasketList_Params=self.BasketList_Params
        )

from firstock.ordersNReport.modifyOrderFunctionality.functions import *


class FirstockModifyOrder:
    def __init__(self, qty, orderNumber, trgprc, product, mkt_protection, prc, tradingSymbol, priceType,userId, retention):
        self.modifyOrder = ApiRequests()
        self.qty = qty
        self.orderNumber = orderNumber
        self.trgprc = trgprc
        self.prc = prc
        self.tradingSymbol = tradingSymbol
        self.priceType = priceType
        self.userId=userId
        self.retention=retention
        self.mkt_protection= mkt_protection
        self.product = product

    def firstockModifyOrder(self):
        result = self.modifyOrder.firstockModifyOrder(qty = self.qty, orderNumber = self.orderNumber, trgprc = self.trgprc, prc = self.prc,
                                                      tradingSymbol = self.tradingSymbol, priceType = self.priceType, userId = self.userId, retention = self.retention, product = self.product, mkt_protection = self.mkt_protection)
        return result

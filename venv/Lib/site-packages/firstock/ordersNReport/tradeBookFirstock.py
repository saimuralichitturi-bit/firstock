from firstock.ordersNReport.tradeBookFunctionality.execution import *


def tradeBook(userId):
    try:
        tradeBook = FirstockTradeBook(userId).firstockTradeBook()
        return tradeBook

    except Exception as e:
        print(e)

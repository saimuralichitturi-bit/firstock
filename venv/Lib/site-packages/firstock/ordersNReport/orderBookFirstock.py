from firstock.ordersNReport.orderBookFunctionality.execution import *


def orderBook(userId):
    try:
        orderBook = FirstockOrderBook(userId).firstockOrderBook()

        return orderBook

    except Exception as e:
        print(e)

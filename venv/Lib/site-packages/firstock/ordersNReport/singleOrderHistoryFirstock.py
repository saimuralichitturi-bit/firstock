from firstock.ordersNReport.singleOrderHistory.execution import *


def singleOrderHistory(orderNumber, userId):
    try:
        singleOrderHistory = FirstockSingleOrderHistory(
            orderNumber=orderNumber,
            userId=userId
        ).firstockSingleOrderHistory()

        return singleOrderHistory

    except Exception as e:
        print(e)

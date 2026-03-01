from firstock.ordersNReport.positionBookFunctionality.execution import *


def positionBook(userId):
    try:

        positionBook = FirstockPositionBook(userId).firstockPositionBook()

        return positionBook

    except Exception as e:
        print(e)
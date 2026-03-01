from firstock.marketConnect.getQuoteLTPFuntionality.execution import *


def getQuoteltp(exchange, tradingSymbol, userId):
    try:
        getQuotes = FirstockGetQuotes(
            exch=exchange,
            token=tradingSymbol,
            userId=userId
        ).firstockGetQuoteLTP()

        return getQuotes

    except Exception as e:
        print(e)

from firstock.marketConnect.getExpiryFunctionality.execution import *


def getExpiry(userId, exchange, tradingSymbol):
    try:
        quoteObj = expiryFirstock(
            userId=userId,
            exchange=exchange,
            tradingSymbol=tradingSymbol
        )

        result = quoteObj.expiryFirstock()
        return result

    except Exception as e:
        print(e)

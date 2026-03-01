from firstock.marketConnect.getQuotesFunctionality.execution import *


def getQuote(exchange, tradingSymbol, userId):
    try:
        getQuotes = FirstockGetQuotes(
            exchange=exchange,
            tradingSymbol=tradingSymbol,
            userId=userId
        ).firstockGetQuotes()

        return getQuotes

    except Exception as e:
        print(e)

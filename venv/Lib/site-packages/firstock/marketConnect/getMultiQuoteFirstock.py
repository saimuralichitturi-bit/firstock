from firstock.marketConnect.getMultiQuoteFunctionality.execution import *


def getMultiQuotes(dataToken, userId):
    try:
        getQuotes = firstockGetMultiQuote(
            dataToken=dataToken,
            userId=userId
        ).firstockGetMultiQuote()

        return getQuotes

    except Exception as e:
        print(e)

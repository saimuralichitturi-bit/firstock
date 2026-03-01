from firstock.marketConnect.getMultiQuoteLTPFuntionality.execution import *


def getMultiQuotesltp(dataToken, userId):
    try:
        getQuotes = firstockGetMultiQuoteLTP(
            dataToken=dataToken,
            userId=userId
        ).firstockGetMultiQuoteLTP()

        return getQuotes

    except Exception as e:
        print(e)

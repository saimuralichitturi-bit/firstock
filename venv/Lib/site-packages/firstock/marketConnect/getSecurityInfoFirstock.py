from firstock.marketConnect.getSecurityInfoFunctionality.execution import *


def securityInfo(tradingSymbol, exchange, userId):
    try:

        securityInfo = FirstockGetSecurityInfo(
            exchange=exchange,
            tradingSymbol=tradingSymbol,
            userId=userId
        ).firstockGetSecurityInfo()

        return securityInfo

    except Exception as e:
        print(e)

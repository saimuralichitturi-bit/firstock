from firstock.marketConnect.getOptionChainFunctionality.execution import *


def optionChain(symbol, exchange, strikePrice, count, userId, expiry):
    try:

        optionChain = FirstockGetOptionChain(
            symbol=symbol,
            exch=exchange,
            strprc=strikePrice,
            cnt=count,
            userId=userId,
            expiry=expiry
        ).firstockGetOptionChain()

        return optionChain

    except Exception as e:
        print(e)

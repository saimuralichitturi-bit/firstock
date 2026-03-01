from firstock.marketConnect.timePriceSeriesFunctionality.execution import *


def timePriceSeries(exchange, tradingSymbol, startTime, endTime, interval, userId):
    try:

        timePrice = FirstockTimePriceSeries(
            exch=exchange,
            tradingSymbol=tradingSymbol,
            st=startTime,
            et=endTime,
            intrv=interval,
            userId=userId
        ).firstockTimePriceSeries()

        return timePrice

    except Exception as e:
        print(e)

from firstock.ordersNReport.holdingsFunctionality.execution import *


def holdings(userId):
    try:

        holding = FirstockHoldings(userId).firstockHoldings()
        return holding

    except Exception as e:
        print(e)


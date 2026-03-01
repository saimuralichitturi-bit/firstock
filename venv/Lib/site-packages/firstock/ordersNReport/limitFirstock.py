from firstock.ordersNReport.limitFunctionality.execution import *


def limit(userId):
    try:

        limits = FirstockLimits(userId).firstockLimits()

        return limits

    except Exception as e:
        print(e)

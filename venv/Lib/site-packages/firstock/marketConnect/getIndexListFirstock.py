from firstock.marketConnect.getIndexListFunctionality.execution import *


def indexList(userId):
    try:
        getIndexList = FirstockGetIndexList(
            userId = userId
        )

        result = getIndexList.firstockGetIndexList()
        return result

    except Exception as e:
        print(e)

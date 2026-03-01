from firstock.marketConnect.searchScripsFunctionality.execution import *


def searchScrips(stext, userId):
    try:

        searchScrips = FirstockSearchScrips(
            stext=stext,
            userId=userId
        ).firstockSearchScrips()

        return searchScrips

    except Exception as e:
        print(e)

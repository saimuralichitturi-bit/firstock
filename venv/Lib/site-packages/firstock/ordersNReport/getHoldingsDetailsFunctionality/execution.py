from firstock.ordersNReport.getHoldingsDetailsFunctionality.functions import *

class FirstockHoldings:
    def __init__(self, userId: str):
        self.holdingsDetails = ApiRequests()
        self.userId = userId

    def getHoldingsDetails(self):
        """
        Executes the getHoldingsDetails request for the user.

        :return: JSON response containing holdings information
        """
        result = self.holdingsDetails.getHoldingsDetails(self.userId)
        return result
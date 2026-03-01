from firstock.ordersNReport.getHoldingsDetailsFunctionality.execution import *

def getHoldingsDetails(userId: str):
    """
    Retrieves holdings details for a user from the Firstock API.

    :param userId: User ID (e.g., "SU2707")
    :return: JSON response containing holdings information
    """
    try:
        holdings = FirstockHoldings(
            userId=userId,
        )

        result = holdings.getHoldingsDetails()

        return result

    except Exception as e:
        print(e)
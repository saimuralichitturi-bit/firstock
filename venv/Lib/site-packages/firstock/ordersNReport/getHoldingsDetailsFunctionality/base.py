from abc import ABC, abstractmethod


class FirstockAPI(ABC):
    @abstractmethod
    def getHoldingsDetails(self, userId: str):
        """
        Retrieves holdings details for a user from the Firstock API.

        :param userId: User ID (e.g., "SU2707")
        :return: JSON response containing holdings information
        """
        pass
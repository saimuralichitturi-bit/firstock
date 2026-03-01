import json
import os
import requests
from firstock.Variables.common_imports import *
from firstock.ordersNReport.getHoldingsDetailsFunctionality.base import *

class ApiRequests(FirstockAPI):
    def getHoldingsDetails(self, userId: str):
        """
        Retrieves holdings details for a user from the Firstock API.

        This method fetches the jKey from config.json and sends a request to the holdingsDetails endpoint.
        The response contains the user's holdings information.

        :param userId: User ID (e.g., "SU2707")
        :return: JSON response from the holdingsDetails request
        """
        # Read jKey from config.json
        config_path = CONFIG_PATH
        if not os.path.exists(config_path):
            return {"status": "failed", "message": "Config file not found"}

        try:
            with open(config_path, "r") as infile:
                config_data = json.load(infile)
        except json.JSONDecodeError:
            return {"status": "failed", "message": "Invalid config file format"}
        except Exception as e:
            return {"status": "failed", "message": f"Error reading config file: {str(e)}"}

        # Retrieve jKey for the given userId
        if userId not in config_data or "jKey" not in config_data[userId]:
            return {"status": "failed", "message": f"No jKey found for userId {userId}"}

        jKey = config_data[userId]["jKey"]

        # Prepare the API request
        url = GETHOLDINGSDETAILS
        payload = {
            "userId": userId,
            "jKey": jKey
        }
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # Raise exception for HTTP errors
            return response.json()
        except requests.RequestException as e:
            return {"status": "failed", "message": str(e)}
        except Exception as e:
            return {"status": "failed", "message": f"Unexpected error: {str(e)}"}
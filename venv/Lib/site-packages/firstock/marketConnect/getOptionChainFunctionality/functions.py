from firstock.Variables.common_imports import *
from firstock.marketConnect.getOptionChainFunctionality.base import *


class ApiRequests(FirstockAPI):
    def firstockGetOptionChain(self, symbol, exch, strprc, cnt, userId, expiry):
        """
        :return:
        """
        url = GETOPTIONCHAIN

        with open(CONFIG_PATH) as file:
            config_data = json.load(file)

        if userId in config_data:
            payload = {
                "userId": userId,
                "exchange": exch,
                "symbol": symbol,
                "strikePrice": strprc,
                "count": cnt,
                "jKey": config_data[userId]['jKey'],
                "expiry" : expiry
            }

            result = requests.post(url, json=payload)
            jsonString = result.content.decode("utf-8")

            finalResult = ast.literal_eval(jsonString)

            return finalResult

        return not_logged_in_user()

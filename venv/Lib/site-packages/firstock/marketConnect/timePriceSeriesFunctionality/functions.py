from firstock.Variables.common_imports import *
from firstock.marketConnect.timePriceSeriesFunctionality.base import *


class ApiRequests(FirstockAPI):
    def firstockTimePriceSeries(self, exch, tradingSymbol, st, et, intrv, userId):
        """
        :return:
        """
        url = TIMEPRICESERIES

        with open(CONFIG_PATH) as file:
            config_data = json.load(file)

        if userId in config_data:
            payload = {
                "userId": userId,
                "exchange": exch,
                "tradingSymbol": tradingSymbol,
                "endTime": et,
                "startTime": st,
                "jKey": config_data[userId]['jKey'],
                "interval": intrv
            }

            result = requests.post(url, json=payload)
            jsonString = result.content.decode("utf-8")

            finalResult = ast.literal_eval(jsonString)

            return finalResult
        return not_logged_in_user()

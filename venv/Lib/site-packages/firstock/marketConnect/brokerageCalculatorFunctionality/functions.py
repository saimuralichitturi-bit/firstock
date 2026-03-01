from firstock.Variables.common_imports import *
from firstock.marketConnect.brokerageCalculatorFunctionality.base import *

class ApiRequests(FirstockAPI):
    def firstockBrokerageCalculator(
        self,
        userId,
        exchange,
        tradingSymbol,
        transactionType,
        product,
        quantity,
        price,
        strike_price,
        inst_name,
        lot_size
    ):
        try:
            url = BROKERAGE_CALCULATOR  # Define this in your constants

            with open(CONFIG_PATH) as file:
                config_data = json.load(file)

            if userId in config_data:
                payload = {
                    "userId": userId,
                    "jKey": config_data[userId]['jKey'],
                    "exchange": exchange,
                    "tradingSymbol": tradingSymbol,
                    "transactionType": transactionType,
                    "Product": product,
                    "quantity": str(quantity),
                    "price": str(price),
                    "strike_price": str(strike_price),
                    "inst_name": inst_name,
                    "lot_size": str(lot_size)
                }

                result = requests.post(url, json=payload)
                jsonString = result.content.decode("utf-8")

                finalResult = ast.literal_eval(jsonString)
                return finalResult

            return not_logged_in_user()

        except Exception as e:
            print(e)

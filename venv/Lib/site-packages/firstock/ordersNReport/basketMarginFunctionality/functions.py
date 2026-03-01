from firstock.Variables.common_imports import *
from firstock.ordersNReport.basketMarginFunctionality.base import *

class ApiRequests(FirstockAPI):
    def firstockBasketMargin(self, userId, exchange, transactionType, product,
                             tradingSymbol, quantity, priceType, price, BasketList_Params):
        try:
            """
            :return: The json response
            """
            url = BASKETMARGIN

            with open(CONFIG_PATH) as file:
                config_data = json.load(file)

            if userId in config_data:
                payload = {
                    "userId": userId,
                    "jKey": config_data[userId]['jKey'],
                    "exchange": exchange,
                    "transactionType": transactionType,
                    "product": product,
                    "tradingSymbol": tradingSymbol,
                    "quantity": quantity,
                    "priceType": priceType,
                    "price": price,
                    "BasketList_Params": BasketList_Params
                }

                result = requests.post(url, json=payload)
                jsonString = result.content.decode("utf-8")
                finalResult = ast.literal_eval(jsonString)
                return finalResult

            return not_logged_in_user()
        except Exception as e:
            print(f"Error in firstockBasketMargin: {e}")




from firstock.Variables.common_imports import *
from firstock.ordersNReport.productConversionFunctionality.base import *


class ApiRequests(FirstockAPI):
    def firstockConvertProduct(self, exch, tsym, qty, prd, prevprd, trantype, postype, userId, msgFlag=None):
        """
        Convert product type for an existing position
        
        :param exch: Exchange
        :param tsym: Trading Symbol
        :param qty: Quantity
        :param prd: Product
        :param prevprd: Previous Product
        :param trantype: Transaction Type
        :param postype: Position Type
        :param userId: User ID
        :param msgFlag: Optional parameter specifying side (Buy/Sell) and position type (Day/CF)
                       "1": Buy and Day
                       "2": Buy and CF
                       "3": Sell and Day
                       "4": Sell and CF
        :return: API response
        """
        try:
            url = PRODUCTCONVERSION

            with open(CONFIG_PATH) as file:
                config_data = json.load(file)

            if userId in config_data:
                payload = {
                    "userId": userId,
                    "exchange": exch,
                    "tradingSymbol": tsym,
                    "quantity": qty,
                    "actid": userId,
                    "product": prd,
                    "previousProduct": prevprd,
                    "transactionType": trantype,
                    "positionType": postype,
                    "jKey": config_data[userId]['jKey']
                }

                # Add msgFlag to payload if provided
                if msgFlag is not None:
                    payload["msgFlag"] = msgFlag

                result = requests.post(url, json=payload)
                jsonString = result.content.decode("utf-8")

                finalResult = ast.literal_eval(jsonString)

                return finalResult
            return not_logged_in_user()

        except Exception as e:
            print(e)
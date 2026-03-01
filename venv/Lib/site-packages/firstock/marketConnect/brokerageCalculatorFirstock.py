from firstock.marketConnect.brokerageCalculatorFunctionality.execution import *


def brokerageCalculator(userId, exchange, tradingSymbol, transactionType,
                                 product, quantity, price, strike_price, inst_name, lot_size):
    try:
        brokerageCalc = FirstockBrokerageCalculator(
            userId=userId,
            exchange=exchange,
            tradingSymbol=tradingSymbol,
            transactionType=transactionType,
            product=product,
            quantity=quantity,
            price=price,
            strike_price=strike_price,
            inst_name=inst_name,
            lot_size=lot_size
        )

        result = brokerageCalc.firstockBrokerageCalculator()
        return result

    except Exception as e:
        print(e)

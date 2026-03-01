from firstock.ordersNReport.basketMarginFunctionality.execution import *

def basketMargin(userId, exchange, transactionType, product,
                          tradingSymbol, quantity, priceType, price,
                          BasketList_Params):
    try:
        placeOrder = FirstockBasketMargin(
            userId=userId,
            exchange=exchange,
            transactionType=transactionType,
            product=product,
            tradingSymbol=tradingSymbol,
            quantity=quantity,
            priceType=priceType,
            price=price,
            BasketList_Params=BasketList_Params
        )

        result = placeOrder.firstockBasketMargin()
        return result

    except Exception as e:
        print(e)

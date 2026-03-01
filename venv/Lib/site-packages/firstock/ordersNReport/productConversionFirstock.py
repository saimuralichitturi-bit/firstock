from firstock.ordersNReport.productConversionFunctionality.execution import *


def productConversion(exchange, tradingSymbol, quantity, product, previousProduct, transactionType, positionType, userId, msgFlag = None):
    try:

        convertProduct = FirstockConvertProduct(
            exch=exchange,
            tsym=tradingSymbol,
            qty=quantity,
            prd=product,
            prevprd=previousProduct,
            trantype=transactionType,
            postype=positionType,
            userId=userId,
            msgFlag=msgFlag

        ).firstockConvertProduct()

        return convertProduct

    except Exception as e:
        print(e)

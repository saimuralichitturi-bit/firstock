from firstock.loginNProfile.loginFunctionality.execution import *


def login(userId, password, TOTP, vendorCode, apiKey):
    try:
        login = FirstockLogin(
            uid=userId,
            pwd=password,
            factor2=TOTP,
            vc=vendorCode,
            appkey=apiKey,
        )

        result = login.firstockLogin()

        return result

    except Exception as e:
        print(e)

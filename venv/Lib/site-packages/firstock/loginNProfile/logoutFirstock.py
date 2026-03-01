from firstock.loginNProfile.logoutFunctionality.execution import *


def logout(userId):
    try:
        logout = FirstockLogout(userId).firstockLogout()
        return logout

    except Exception as e:
        print(e)

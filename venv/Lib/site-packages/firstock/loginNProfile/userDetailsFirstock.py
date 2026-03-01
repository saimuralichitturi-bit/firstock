from firstock.loginNProfile.userDetailsFunctionality.execution import *


def userDetails(userId):
    try:
        userDetails = FirstockUserDetails(userId).firstockUserDetails()

        return userDetails

    except Exception as e:
        print(e)

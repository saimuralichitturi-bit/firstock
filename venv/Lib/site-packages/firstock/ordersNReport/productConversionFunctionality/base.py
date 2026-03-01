from abc import ABC, abstractmethod


class FirstockAPI(ABC):
    @abstractmethod
    def firstockConvertProduct(self, exch, tsym, qty, prd, prevprd, trantype, postype, userId, msgFlag=None):
        """
        :return:
        """
        pass

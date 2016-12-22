# -*- coding:utf-8 -*-
# Create On 20161222
# Auth: wang.yijian
# desc: 交易日历

import sys;sys.path.append("../")
import utils.dateTime as dateTime


class CTradingCalendar(object):
    __dictTc = {}

    def Empty(self):
        if (len(self.__dictTc) == 0):
            return True
        else:
            return False

    # Set && Get
    def Add(self, strExchange, setTc):
        self.__dictTc[strExchange] = setTc

    def GetAll(self):
        return self.__dictTc

    def Get(self, strExchange):
        if (strExchange in self.__dictTc):
            return self.__dictTc[strExchange]
        else:
            return None

    def IsTradingDay(self, strExchange, tradingDay):
        nTd = 0
        if (isinstance(tradingDay,int)):
            nTd = tradingDay
        elif (dateTime.isValidDate_IsoExt(tradingDay)):
            nTd = int(dateTime.DateFormat_IsoExt2Iso(tradingDay))
            pass
        elif (dateTime.isValidDate_Iso(tradingDay)):
            nTd = int(tradingDay)
            pass
        else:
            return False

        if (strExchange in self.__dictTc == False):
            return False
        return nTd in self.__dictTc[strExchange]

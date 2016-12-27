# -*- coding:utf-8 -*-
# Create On 20161222
# Auth: wang.yijian
# desc: 行情K线

import sys;sys.path.append("../")

from enum import Enum
import time

# Enum
class EU_MdBarInterval(Enum):
        mdbi_none = 0
        mdbi_1m = 1
        mdbi_5m = 5
        mdbi_15m = 15
        mdbi_30m = 30
        mdbi_60m = 60
        mdbi_1d = 100
        mdbi_5d = 500
        mdbi_10d = 1000
        mdbi_20d = 2000
        mdbi_60d = 6000
        mdbi_120d = 12000


class CMdBarData(object):
    def __init__(self, euMdBi, dOpenPrice, dHighPrice, dLowPrice, dClosePrice, dPreClosePrice, nVolume, dTurnOver, dtDateTime):
        self.__euMdBi = euMdBi
        self.__dOpen = dOpenPrice
        self.__dHigh = dHighPrice
        self.__dLow = dLowPrice
        self.__dClose = dClosePrice
        self.__dPreClose = dPreClosePrice
        self.__nVolume = nVolume
        self.__dTurnOver = dTurnOver
        self.__dtDateTime = dtDateTime
    def GetPrice(self):
        return self.__dOpen, self.__dHigh, self.__dLow, self.__dClose, self.__dPreClose
    def GetVolume(self):
        return self.__nVolume, self.__dTurnOver
    def GetDateTime(self):
        return self.__dtDateTime
    def GetInterval(self):
        return self.__euMdBi


class CMdBarDataManager(object):
    __dictMdBarData = {}    # euMdBi -> nStockId -> tradingDay -> CMdbarData

    def __init__(self):
        pass

    def Add(self, nStockId, mdBarData):
        if (isinstance(nStockId, int) == False or isinstance(mdBarData, CMdBarData) == False):
            return False
        euMdBi = mdBarData.GetInterval()
        if (euMdBi not in self.__dictMdBarData.keys()):
            self.__dictMdBarData[euMdBi] = {}
        if (nStockId not in self.__dictMdBarData[euMdBi]):
            self.__dictMdBarData[euMdBi][nStockId] = {}
        dtDateTime = mdBarData.GetDateTime()
        # if (dtDateTime not in self.__dictMdBarData[nStockId][nStockId]):
        #     self.__dictMdBarData[nStockId][nStockId][dtDateTime] = None
        self.__dictMdBarData[euMdBi][nStockId][dtDateTime] = mdBarData
        for key1 in self.__dictMdBarData.keys():
            for key2 in self.__dictMdBarData[key1].keys():
                for key3 in self.__dictMdBarData[key1][key2].keys():
                    print(self.__dictMdBarData[key1][key2][key3].GetInterval, self.__dictMdBarData[key1][key2][key3].GetPrice())
        return True
        pass

# print(time.strftime("%Y-%m-%d", time.localtime(time.time())))
# print(time.time())
# print(time.localtime(time.time()))
# print(time.localtime(time.time()).time())

# datetime.
'''
mdBarData = CMdBarData(EU_MdBarInterval.mdbi_1d, 10.0, 12.1, 9.98, 9.99, 10.1, 100, 100323, time.time())
mdbarMgr = CMdBarDataManager()
print(mdbarMgr.Add(610060, mdBarData))
mdBarData = CMdBarData(EU_MdBarInterval.mdbi_1d, 23.0, 24.1, 21.98, 22.99, 20.1, 3320, 3340323, time.time())
print(mdbarMgr.Add(610070, mdBarData))
'''
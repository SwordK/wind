# -*- coding:utf-8 -*-
# Create On 20161222
# Auth: wang.yijian
# desc: 行情K线

import sys;sys.path.append("../")
import time
import datetime
from enum import Enum

import business.stockCn as stockCn
import utils.dateTime as dateTime

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
    __dictMdBarData = {}    # euMdBi -> nStockId -> tradingDay<datetime> -> CMdbarData

    def __init__(self):
        pass

    def Clear(self):
        self.__dictMdBarData.clear()

    # 删除dtBefore 之前的记录
    def RemoveBefore(self, inputBefore):
        dtBefore = inputBefore
        print(1)
        if (isinstance(inputBefore, datetime.datetime) == False):
            print(2)
            dtBefore = dateTime.ToDateTime(inputBefore)
            if (dtBefore == None):
                print(3, dtBefore, inputBefore)
                return False
        print(4)
        for keyMdbi in list(self.__dictMdBarData.keys()):
            for keyStockId in list(self.__dictMdBarData[keyMdbi].keys()):
                for keyTd in list(self.__dictMdBarData[keyMdbi][keyStockId].keys()):
                    if (keyTd < dtBefore):
                        del self.__dictMdBarData[keyMdbi][keyStockId][keyTd]
        print(5)
        # self.Print()
        pass

    def Add(self, strStockWindCode, mdBarData):
        nStockId = stockCn.StockWindCode2Int(strStockWindCode)
        if (nStockId == None):
            return False
        if (isinstance(mdBarData, CMdBarData) == False):
            return False

        euMdBi = mdBarData.GetInterval()
        if (euMdBi not in self.__dictMdBarData.keys()):
            self.__dictMdBarData[euMdBi] = {}
        if (nStockId not in self.__dictMdBarData[euMdBi]):
            self.__dictMdBarData[euMdBi][nStockId] = {}

        dtDateTime = dateTime.ToDateTime(mdBarData.GetDateTime())
        if (dtDateTime == None):
            return False
        self.__dictMdBarData[euMdBi][nStockId][dtDateTime] = mdBarData
        return True

    def GetPrice(self, euMdbi, strStockWindCode, strTradingDay):
        dtDateTime = dateTime.ToDateTime(strTradingDay)
        nStockId = stockCn.StockWindCode2Int(strStockWindCode)
        if (self.__IsIn(euMdbi, nStockId, dtDateTime) == False):
            return None
        return self.__dictMdBarData[euMdbi][nStockId][dtDateTime].GetPrice()

    def GetVolume(self, euMdbi, strStockWindCode, strTradingDay):
        dtDateTime = dateTime.ToDateTime(strTradingDay)
        nStockId = stockCn.StockWindCode2Int(strStockWindCode)
        if (self.__IsIn(euMdbi, nStockId, dtDateTime) == False):
            return None
        return self.__dictMdBarData[euMdbi][nStockId][dtDateTime].GetVolume()

    def Print(self):
        for key1 in self.__dictMdBarData.keys():
            for key2 in self.__dictMdBarData[key1].keys():
                for key3 in self.__dictMdBarData[key1][key2].keys():
                    print(key1, key2, key3, self.__dictMdBarData[key1][key2][key3].GetInterval(), self.__dictMdBarData[key1][key2][key3].GetPrice())

    def __IsIn(self, euMdbi, strStockWindCode, strTradingDay):
        nStockId = stockCn.StockWindCode2Int(strStockWindCode)
        if (nStockId == None):
            print('nStockId is None')
            return False
        dtDateTime = dateTime.ToDateTime(strTradingDay)
        if (dtDateTime == None):
            print('dtDateTime is None')
            return False
        if (euMdbi not in self.__dictMdBarData.keys()):
            print('euMdbi is not in: ', euMdi, self.__dictMdBarData.keys())
            return False
        if (nStockId not in self.__dictMdBarData[euMdbi].keys()):
            # print('nStockId is not in: ', nStockId, self.__dictMdBarData[euMdbi].keys())
            return False
        if (dtDateTime not in self.__dictMdBarData[euMdbi][nStockId].keys()):
            # print('dtDateTime is not in: ', dtDateTime, strStockWindCode, self.__dictMdBarData[euMdbi][nStockId].keys())
            return False
        return True


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
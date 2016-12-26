# -*- coding:utf-8 -*-
# Create On 20161222
# Auth: wang.yijian
# desc: 股票池

import sys;sys.path.append("../")

from enum import Enum
import datetime

import utils.dateTime as dateTime

# Enum
class EU_StockPoolType(Enum):
    euspt_None = -1
    euspt_All = 0
    euspt_SZ50 = 50
    euspt_HS300 = 300
    euspt_ZZ500 = 500
    euspt_ZZ800 = 800

# Functions
def GetStockPoolWindCode(euspt):
    if (isinstance(euspt, EU_StockPoolType) == False):
        return False
    switcher = {
        EU_StockPoolType.euspt_None: 'None',
        EU_StockPoolType.euspt_All: 'All',
        EU_StockPoolType.euspt_SZ50: '000016.SH',
        EU_StockPoolType.euspt_HS300: '000300.SH',
        EU_StockPoolType.euspt_ZZ500: '000905.SH',
        EU_StockPoolType.euspt_ZZ800: '000906.SH',
    }
    return switcher.get(euspt, 'Nothing')


class CStockPoolElem(object):
    def __init__(self, strStockWindCode, nInDate, nOutDate, nIsIn):
        self.__strStockWindCode = strStockWindCode
        self.__nInDate = nInDate
        self.__nOutDate = nOutDate
        self.__nIsIn = nIsIn

    def GetStockWindCode(self):
        return self.__strStockWindCode
    def GetInDate(self):
        return self.__nInDate
    def GetOutDate(self):
        return self.__nOutDate


class CStockPool(object):
    def __init__(self, euSpt):
        self.__euSpt = euSpt
        self.__dictSpElems = {}
        self.__dictSpElemsByTd = {}

    def GetType(self):
        return self.__euSpt

    def GetStocksByTd(self, inputDate):
        strTd = dateTime.ToIso(inputDate)
        if (strTd == None or strTd == ''):
            return None
        nTd = int(strTd)
        if (nTd in self.__dictSpElemsByTd.keys()):
            return self.__dictSpElemsByTd[nTd]
        else:
            return None

    def AddElem(self, spElem):
        if (isinstance(spElem, CStockPoolElem) == False):
            return False
        strWindCode = spElem.GetStockWindCode()
        if ((strWindCode in self.__dictSpElems.keys()) == False):
            self.__dictSpElems[strWindCode] = list()
        self.__dictSpElems[strWindCode].append(spElem)
        return True

    def GenerateTdIndex(self):
        nLoopIndex = 0
        for strStock, listElems in self.__dictSpElems.items():
            print(nLoopIndex, '/', len(self.__dictSpElems))
            nLoopIndex += 1
            for elem in listElems:
                nInDate = elem.GetInDate()
                nOutDate = elem.GetOutDate()

                nLoopDate = nInDate
                while (nLoopDate <= nOutDate):
                    if ((nLoopDate in self.__dictSpElemsByTd) == False):
                        self.__dictSpElemsByTd[nLoopDate] = list()
                        print('add index ', nLoopDate)

                    self.__dictSpElemsByTd[nLoopDate].append(strStock)
                    # Next Date
                    dateLoopDate = dateTime.ToDateTime(nLoopDate)
                    dateTomorrow = dateLoopDate + datetime.timedelta(days=1)
                    nLoopDate = int(dateTime.ToIso(dateTomorrow))


class CStockPoolManager(object):
    __dictStockPools = {}

    def GetStockPool(self, euSpt):
        if (isinstance(euSpt, EU_StockPoolType) == False):
            return None
        if euSpt in self.__dictStockPools:
            return self.__dictStockPools[euSpt]
        else:
            spInst = CStockPool(euSpt)
            self.__dictStockPools[euSpt] = spInst
            return self.__dictStockPools[euSpt]

    def SetStockPool(self, spInst):
        if (isinstance(spInst, CStockPool) == False):
            return False
        euSpt = spInst.GetType()
        self.__dictStockPools[euSpt] = spInst
        return True

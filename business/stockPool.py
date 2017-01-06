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

def GetSupportedSp():
    return 'SZ50|HS300|ZZ500|ZZ800|All'

def GetStockPoolByStr(strInput):
    if (strInput == 'SZ50'):
        return EU_StockPoolType.euspt_SZ50
    elif (strInput == 'HS300'):
        return EU_StockPoolType.euspt_HS300
    elif (strInput == 'ZZ500'):
        return EU_StockPoolType.euspt_ZZ500
    elif (strInput == 'ZZ800'):
        return EU_StockPoolType.euspt_ZZ800
    elif (strInput == 'All'):
        return EU_StockPoolType.euspt_All
    else:
        return EU_StockPoolType.euspt_None


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
    # @param:  nStockId: int
    #          nInDate: int
    #          nOutDate: int
    #          nIsIn: int
    def __init__(self, nStockId, nInDate, nOutDate, nIsIn):
        self.__nStockId = stockCn.StockWindCode2Int(nStockId)
        strInDate = dateTime.ToIso(nInDate)
        strOutDate = dateTime.ToIso(nOutDate)
        if (strInDate == None or strOutDate == None):
            return None
        self.__nInDate = int(strInDate)
        self.__nOutDate = int(strOutDate)
        self.__nIsIn = nIsIn

    def GetStockId(self):
        return self.__nStockId
    def GetInDate(self):
        return self.__nInDate
    def GetOutDate(self):
        return self.__nOutDate


class CStockPool(object):
    def __init__(self, euSpt):
        self.__euSpt = euSpt
        self.__dictSpElems = {}         # nStockId<int>   -> list<CStockPoolElem>
        self.__dictSpElemsByTd = {}     # tradingDay<int> -> list<nStockId>

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

    # @param
    # @return: set<nStockId>
    def GetStocksByDatePeriod(self, dtFrom, dtTo):
        dtPeriod = dateTime.CDatePeriod(dtFrom, dtTo)
        setRtn = set()
        for dtLoop in dtPeriod.DateList():
            listLoop = self.GetStocksByTd(dtLoop)
            if (listLoop == None):
                continue
            for dtElem in listLoop:
                setRtn.add(dtElem)
        return sorted(setRtn)


    def AddElem(self, spElem):
        if (isinstance(spElem, CStockPoolElem) == False):
            return False
        nStockId = spElem.GetStockId()
        if ((nStockId in self.__dictSpElems.keys()) == False):
            self.__dictSpElems[nStockId] = list()
        self.__dictSpElems[nStockId].append(spElem)
        return True

    def GenerateTdIndex(self):
        print('CStockPoolManager.GenerateTdIndex ...')
        nLoopIndex = 0
        nShowPercent = 0
        for nStockId, listElems in self.__dictSpElems.items():
            nLoopPercent = int(nLoopIndex * 100 / len(self.__dictSpElems))
            if (nShowPercent < nLoopPercent and nLoopPercent % 10 == 0):
                nShowPercent = int(nLoopIndex * 100 / len(self.__dictSpElems))
                print(str(nShowPercent) + '%')
            # print(nLoopIndex, '/', len(self.__dictSpElems))
            nLoopIndex += 1

            for elem in listElems:
                nInDate = elem.GetInDate()
                nOutDate = elem.GetOutDate()

                nLoopDate = nInDate
                while (nLoopDate <= nOutDate):
                    if ((nLoopDate in self.__dictSpElemsByTd) == False):
                        self.__dictSpElemsByTd[nLoopDate] = list()
                    self.__dictSpElemsByTd[nLoopDate].append(nStockId)
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

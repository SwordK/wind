# -*- coding:utf-8 -*-
# Create On 20161222
# Auth: wang.yijian
# desc: 行业

import sys;sys.path.append("../")
from enum import Enum
import business.stockCn as stockCn
import utils.dateTime as dateTime

# Enum 行业中性
class EU_IndustrialNeutralType(Enum):
    euInt_None = 0
    euInt_Common = 1
    euInt_OlsResidualError = 2          # 最小二乘法残差

def GetIndustrialNeutralTypeByStr(strInput):
    if (strInput == 'common'):
        return EU_IndustrialNeutralType.euInt_Common
    elif (strInput == 'ols'):
        return EU_IndustrialNeutralType.euInt_OlsResidualError
    else:
        return EU_IndustrialNeutralType.euInt_None

class CIndustryBaseInfo(object):
    @staticmethod
    def ToLevel1Code_Static(strIndustryCode):
        if (len(strIndustryCode) < 4):
            return None
        strL1Code = strIndustryCode[0:4] + '000000'
        return strL1Code

    def __init__(self, strIndustryCode, strName, strAlias, nLevel, nUsed):
        self.__strIndustryCode = strIndustryCode
        self.__strName = strName
        self.__strAlias = strAlias
        self.__nLevel = nLevel
        self.__nUsed = nUsed

    def GetICode(self):
        return self.__strIndustryCode
    def GetLevel(self):
        return self.__nLevel

    def ToLevel1Code(self):
        return CIndustryBaseInfo.ToLevel1Code_Static(self.__strIndustryCode)


class CIndustryBaseInfoManager(object):
    __dictIBaseInfos = {}           # key: ICode, value: list of CIndustryBaseInfo object
    __dictIBaseInfosByLevel = {}    # key: level, value: dict: key1 = IndustruyCode, CIndustryBaseInfo object
    def __init__(self):
        pass

    def Add(self, industryInst):
        if (isinstance(industryInst, CIndustryBaseInfo) == False):
            return False
        self.__dictIBaseInfos[industryInst.GetICode()] = industryInst
        if (industryInst.GetLevel() not in self.__dictIBaseInfosByLevel):
            self.__dictIBaseInfosByLevel[industryInst.GetLevel()] = {}
        self.__dictIBaseInfosByLevel[industryInst.GetLevel()][industryInst.GetICode()] = industryInst
        return True


class CStockIndustryPeriod(object):
    def __init__(self, strStockWindCode, strICode):
        self.__strStockWindCode = strStockWindCode
        self.__strICode = strICode
        self.__listPeriod = []

    def Add(self, dtFrom, dtTo):
        dpInst = dateTime.CDatePeriod(dtFrom, dtTo)
        if (dpInst.IsValid()):
            self.__listPeriod.append(dpInst)
            return True
        else:
            return False

    def GetStockWindCode(self):
        return self.__strStockWindCode
    def GetICode(self):
        return self.__strICode
    def GetPeriods(self):
        return self.__listPeriod


class CStockIndustryPeriodManager(object):
    __dictSipL1 = {}            # ICode -> stockWindCode -> CStockIndustryPeriod object
    __dictSipL1BySid = {}       # stockWindCode -> ICode -> CStockIndustryPeriod object
    __dictSipL1ByTd1 = {}       # tradingDay -> ICode -> list of stockWindCode
    __dictSipL1ByTd2 = {}       # tradingDay -> stockWindCode -> list of ICode


    def AddPeriod(self, strStockWindCode, strICode, nFromDate, nToDate):
        if (strICode not in self.__dictSipL1.keys()):
            self.__dictSipL1[strICode] = {}
        nStockId = stockCn.StockWindCode2Int(strStockWindCode)
        if (nStockId == None):
            return False

        if (nStockId not in self.__dictSipL1[strICode].keys()):
            self.__dictSipL1[strICode][nStockId] = CStockIndustryPeriod(nStockId, strICode)
        bRtnAdd = self.__dictSipL1[strICode][nStockId].Add(nFromDate, nToDate)
        if (bRtnAdd == False):
            return False
        else:
            if (nStockId not in self.__dictSipL1BySid.keys()):
                self.__dictSipL1BySid[nStockId] = {}
            self.__dictSipL1BySid[nStockId][strICode] = self.__dictSipL1[strICode][nStockId]
            return True

    def GenerateTdIndex(self, dtFrom, dtTo):
        strFrom = dateTime.ToIso(dtFrom)
        strTo = dateTime.ToIso(dtTo)
        if (strFrom == '' or strFrom == None or strTo == '' or strTo == None):
            return False
        inputPeriod = dateTime.CDatePeriod(strFrom, strTo)

        for strICode in self.__dictSipL1.keys():
            for nStockId in self.__dictSipL1[strICode]:
                # self.__dictSipL1BySid[nStockId] = {}
                # self.__dictSipL1BySid[nStockId][strICode] = self.__dictSipL1[strICode][nStockId]
                for period in self.__dictSipL1[strICode][nStockId].GetPeriods():
                    dpIntersection = inputPeriod.Intersection(period)
                    if (dpIntersection == None):
                        continue
                    # for dtDay in dpIntersection.DateList():
                    #     if dtDay not in self.__dictSipL1ByTd1:
                    #         self.__dictSipL1ByTd1[dtDay] = {}
                    #     if strICode not in self.__dictSipL1ByTd1[dtDay]:
                    #         self.__dictSipL1ByTd1[dtDay][strICode] = []
                    #     self.__dictSipL1ByTd1[dtDay][strICode].append(nStockId)
#
                    #     if dtDay not in self.__dictSipL1ByTd2:
                    #         self.__dictSipL1ByTd2[dtDay] = {}
                    #     if strICode not in self.__dictSipL1ByTd2[dtDay]:
                    #         self.__dictSipL1ByTd2[dtDay][nStockId] = []
                    #     self.__dictSipL1ByTd2[dtDay][nStockId].append(strICode)

    def Print__dictSipL1(self):
        for strICode in self.__dictSipL1.keys():
            for strStockWindCode in self.__dictSipL1[strICode]:
                for period in self.__dictSipL1[strICode][strStockWindCode].GetPeriods():
                    print(strStockWindCode, strICode, period.From(), period.To())


    def Print__dictSipL1BySid(self):
        for strStockWindCode in self.__dictSipL1BySid.keys():
            for strICode in self.__dictSipL1BySid[strStockWindCode]:
                for period in self.__dictSipL1BySid[strStockWindCode][strICode].GetPeriods():
                    print(strStockWindCode, strICode, period.From(), period.To())

    def Print____dictSipL1ByTd1(self):
        for td in self.__dictSipL1ByTd1.keys():
            for strICode in self.__dictSipL1ByTd1[td]:
                print(td, strICode, self.__dictSipL1ByTd1[td][strICode])

    def Print____dictSipL1ByTd2(self):
        for td in self.__dictSipL1ByTd2.keys():
            for strStockWindCode in self.__dictSipL1ByTd2[td]:
                print(td, strStockWindCode, self.__dictSipL1ByTd2[td][strStockWindCode])




class CStockIndustryPeriodr_Pandas(object):    
    __dfData = {}
    __colIn = 'IN_DATE'
    __colOut = 'OUT_DATE'
    __colCurSign = 'CUR_SIGN'
    __colIndCode = 'CITICS_IND_CODE'

    def SetData(self, dfData):
        self.__dfData[0] = dfData

    def GetStockIndustry(self, inputTradingDay, strStock):
        dtTradingDay = dateTime.ToDateTime(inputTradingDay)
        strSi = '-'
        if strStock in self.__dfData[0].index:        
            dfStock = self.__dfData[0].ix[strStock]
            nIdxLen = len(dfStock.index)

            nIndex = 0
            while nIndex < nIdxLen:
                dfLoop = dfStock.ix[nIndex]
                nIndex += 1
                dtIn = dateTime.ToDateTime(dfLoop[self.__colIn])
                if (dtTradingDay < dtIn):
                    continue
                else:
                    if dfLoop[self.__colCurSign] == '1' or dtTradingDay <= dateTime.ToDateTime(dfLoop[self.__colOut]):
                        strSi = dfLoop[self.__colIndCode]
                        break
        return strSi
    
    def Print(self):
        print(self.__dfData)

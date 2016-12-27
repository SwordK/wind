# -*- coding:utf-8 -*-
# Create On 20161222
# Auth: wang.yijian
# desc: 行业

import sys;sys.path.append("../")
import utils.dateTime as dateTime

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
        if (strStockWindCode not in self.__dictSipL1[strICode].keys()):
            self.__dictSipL1[strICode][strStockWindCode] = CStockIndustryPeriod(strStockWindCode, strICode)
        return self.__dictSipL1[strICode][strStockWindCode].Add(nFromDate, nToDate)

    def GenerateTdIndex(self, dtFrom, dtTo):
        strFrom = dateTime.ToIso(dtFrom)
        strTo = dateTime.ToIso(dtTo)
        if (strFrom == '' or strFrom == None or strTo == '' or strTo == None):
            return False
        inputPeriod = dateTime.CDatePeriod(strFrom, strTo)

        for strICode in self.__dictSipL1.keys():
            for strStockWindCode in self.__dictSipL1[strICode]:
                self.__dictSipL1BySid[strStockWindCode] = {}
                self.__dictSipL1BySid[strStockWindCode][strICode] = self.__dictSipL1[strICode][strStockWindCode]
                for period in self.__dictSipL1[strICode][strStockWindCode].GetPeriods():
                    dpIntersection = inputPeriod.Intersection(period)
                    if (dpIntersection == None):
                        continue
                    # for dtDay in dpIntersection.DateList():
                    #     if dtDay not in self.__dictSipL1ByTd1:
                    #         self.__dictSipL1ByTd1[dtDay] = {}
                    #     if strICode not in self.__dictSipL1ByTd1[dtDay]:
                    #         self.__dictSipL1ByTd1[dtDay][strICode] = []
                    #     self.__dictSipL1ByTd1[dtDay][strICode].append(strStockWindCode)
#
                    #     if dtDay not in self.__dictSipL1ByTd2:
                    #         self.__dictSipL1ByTd2[dtDay] = {}
                    #     if strICode not in self.__dictSipL1ByTd2[dtDay]:
                    #         self.__dictSipL1ByTd2[dtDay][strStockWindCode] = []
                    #     self.__dictSipL1ByTd2[dtDay][strStockWindCode].append(strICode)

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



# -*- coding:utf-8 -*-
# Create On 20161222
# Auth: wang.yijian
# desc: 行业

import sys;sys.path.append("../")


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
    __dictIBaseInfos = {}
    __dictIBaseInfosByLevel = {}
    def __init__(self):
        pass

    def Add(self, industryInst):
        if (isinstance(industryInst, CIndustryBaseInfo) == False):
            return False
        self.__dictIBaseInfos[industryInst.GetICode()] = industryInst
        self.__dictIBaseInfosByLevel[industryInst.GetLevel()] = industryInst
        return True

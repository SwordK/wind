# -*- coding:utf-8 -*-
# Create On 20161221
# Auth: wang.yijian
# desc: 日期时间相关

import time
import datetime

# YYYY-MM-DD
# @param: str: [isoext]
def isValidDate_IsoExt(str):
    try:
        if (len(str) != 10):
            return False
        time.strptime(str, "%Y-%m-%d")
        return True
    except:
        return False

# YYYYMMDD
# @param: str: [iso]
def isValidDate_Iso(str):
    '''判断是否是一个有效的日期字符串'''
    try:
        if (len(str) != 8):
            return False
        time.strptime(str, "%Y%m%d")
        return True
    except:
        return False

# @param: strIso: [iso]
def DateFormat_Iso2IsoExt(strIso):
    if (isValidDate_Iso(strIso) == False):
        return None
    timeArray = time.strptime(strIso, "%Y%m%d")
    return time.strftime("%Y-%m-%d", timeArray)

# @param: strIsoExt: [isoext]
def DateFormat_IsoExt2Iso(strIsoExt):
    if (isValidDate_IsoExt(strIsoExt) == False):
        return None
    timeArray = time.strptime(strIsoExt, "%Y-%m-%d")
    return time.strftime("%Y%m%d", timeArray)

# @param: inputDate: [datetime.date/int/iso/isoext]
def ToIso(inputDate):
    strDate = inputDate
    if (isinstance(inputDate, datetime.date)):
        strDate = inputDate.strftime('%Y%m%d')
        return strDate

    if (isinstance(inputDate, int)):
        strDate = str(inputDate)
    if (strDate != ''):
        if (isValidDate_IsoExt(strDate)):
            return DateFormat_IsoExt2Iso(strDate)
        elif (isValidDate_Iso(strDate)):
            return strDate
        else:
            return None
    return ''

# @param: inputDate: [datetime.date/int/iso/isoext]
def ToIsoExt(inputDate):
    strDate = inputDate
    if (isinstance(inputDate, datetime.date)):
        strDate = inputDate.strftime('%Y-%m-%d')
        return strDate

    if (isinstance(inputDate, int)):
        strDate = str(inputDate)
    if (strDate != ''):
        if (isValidDate_IsoExt(strDate)):
            return strDate
        elif (isValidDate_Iso(strDate)):
            return DateFormat_Iso2IsoExt(strDate)
        else:
            return None
    return ''

# @param: inputDate: [int/iso/isoext]
def ToDateTime(inputDate):
    strDate = inputDate
    if (isinstance(inputDate, int)):
        strDate = str(inputDate)

    if (strDate != ''):
        if (isValidDate_IsoExt(strDate)):
            return datetime.datetime.strptime(strDate, "%Y-%m-%d")
        elif (isValidDate_Iso(strDate)):
            return datetime.datetime.strptime(strDate, "%Y%m%d")
        else:
            return None

# @param: inputDate: [int/iso/isoext]
# @return: iso date
def Tomorrow(inputDate):
    dateLoopDate = ToDateTime(inputDate)
    if (dateLoopDate == None):
        return None
    dateTomorrow = dateLoopDate + datetime.timedelta(days=1)
    return ToIso(dateTomorrow)



# print(isValidDate_IsoExt('2016-12-31'))
# print(isValidDate_IsoExt('2016-2-2'))
# print(isValidDate_IsoExt('2016-02-29'))
# print(isValidDate_IsoExt('20161231'))
# print(isValidDate_IsoExt('2016-12-32'))
# print(isValidDate_IsoExt('2015-02-29'))

# print(isValidDate_Iso('20160202'))
# print(isValidDate_Iso('20160229'))
# print(isValidDate_Iso('20150229'))
# print(isValidDate_Iso('2016-02-02'))
# print(isValidDate_Iso('2016202'))

# print(DateFormat_Iso2IsoExt('20100203'))
# print(DateFormat_IsoExt2Iso('2010-02-03'))

# print(ToIso('2016-02-29'))
# print(ToIsoExt('20160229'))

# print(ToDateTime(20160229))
# print(ToDateTime('20160229'))
# print(ToDateTime('2016-02-29'))

# print(Tomorrow(20121212))
# print(Tomorrow('20121212'))
# print(Tomorrow('2012-12-31'))
# print(Tomorrow('2012-12-32'))
#

class CDatePeriod(object):
    def __init__(self, dtFrom, dtTo):
        self.__nFrom = 0
        self.__nTo = 0
        strFrom = ToIso(dtFrom)
        strTo = ToIso(dtTo)
        if (strFrom == '' or strFrom == None or strTo == '' or strTo == None):
            return
        self.__nFrom = int(strFrom)
        self.__nTo = int(strTo)
        if (self.__nFrom > self.__nTo):
            self.__nFrom = int(strTo)
            self.__nTo = int(strFrom)
        if (self.IsValid() == False):
            return False
        self.__listDate = []
        nLoopDate = self.__nFrom
        while (nLoopDate  <= self.__nTo):
            self.__listDate.append(nLoopDate)
            strLoopDate = Tomorrow(nLoopDate)
            nLoopDate = int(strLoopDate)

    def IsValid(self):
        return (self.__nFrom != 0 and self.__nTo != 0)

    def From(self):
        return self.__nFrom
    def To(self):
        return self.__nTo

    # 获取日期区间内的所有日期
    def DateList(self):
        return self.__listDate

    def IsInPeriod(self, inputDate):
        strInputDate = ToIso(inputDate)
        if (strInputDate == None or strInputDate == ''):
            return False
        nInputDate = int(strInputDate)
        if (nInputDate >= self.__nFrom and nInputDate <= self.__nTo):
            return True
        else:
            return False

    # 求交集
    def Intersection(self, dpRhs):
        if (isinstance(dpRhs, CDatePeriod) == False):
            return None
        nFromRhs = dpRhs.From()
        nToRhs = dpRhs.To()
        nFromNew = max(nFromRhs, self.__nFrom)
        nToNew = min(nToRhs, self.__nTo)
        if (nFromNew > nToNew):
            return None
        return CDatePeriod(nFromNew, nToNew)

'''
# Test CDatePeriod.Intersection()
dp1 = CDatePeriod(20160101, 20161231)
dp = CDatePeriod(20150101, 20151231)
dpR = dp1.Intersection(dp)
if (dpR == None):
    print(dpR)
else:
    print(dpR.From(), dpR.To())

dp = CDatePeriod(20170101, 20171231)
dpR = dp1.Intersection(dp)
if (dpR == None):
    print(dpR)
else:
    print(dpR.From(), dpR.To())

dp = CDatePeriod(20150101, 20171231)
dpR = dp1.Intersection(dp)
if (dpR == None):
    print(dpR)
else:
    print(dpR.From(), dpR.To())

dp = CDatePeriod(20160401, 20161201)
dpR = dp1.Intersection(dp)
if (dpR == None):
    print(dpR)
else:
    print(dpR.From(), dpR.To())

dp = CDatePeriod(20150101, 20161201)
dpR = dp1.Intersection(dp)
if (dpR == None):
    print(dpR)
else:
    print(dpR.From(), dpR.To())

dp = CDatePeriod(20160301, 20171231)
dpR = dp1.Intersection(dp)
if (dpR == None):
    print(dpR)
else:
    print(dpR.From(), dpR.To())
'''
# -*- coding:utf-8 -*-
# Create On 20161221
# Auth: wang.yijian
# desc: 日期时间相关

# import time
import datetime

# ##############################################################################
# YYYY-MM-DD
# @param:  str: [isoext]
# @return: BOOL, datetime
def isValidDate_IsoExt(str):
    dtRtn = None
    if (len(str) != 10):
        return False, dtRtn
    try:
        dtRtn = datetime.datetime.strptime(str, "%Y-%m-%d")
        return True, dtRtn
    except:
        return False, dtRtn

# YYYYMMDD
# @param: str: [iso]
# @return: BOOL, datetime
def isValidDate_Iso(str):
    dtRtn = None
    if (len(str) != 8):
        return False, dtRtn
    try:
        dtRtn = datetime.datetime.strptime(str, "%Y%m%d")
        return True, dtRtn
    except:
        return False, dtRtn

def isValidDate(str):
    bCheck, timeArray = isValidDate_Iso(str)
    if (bCheck == False or timeArray == None):
        bCheck, timeArray = isValidDate_IsoExt(str)
        if (bCheck == False or timeArray == None):
            return False, None
    return True, timeArray


# ##############################################################################
# @param: strIso: [iso]
def DateFormat_Iso2IsoExt(strIso):
    bCheck, timeArray = isValidDate_Iso(strIso)
    if (bCheck == False or timeArray == None):
        return None
    strRtn = "%04d-%02d-%02d" % (timeArray.date().year, timeArray.date().month, timeArray.date().day)
    return strRtn

# @param: strIsoExt: [isoext]
def DateFormat_IsoExt2Iso(strIsoExt):
    bCheck, timeArray = isValidDate_IsoExt(strIsoExt)
    if (bCheck == False or timeArray == None):
        return None
    strRtn = "%04d-%02d-%02d" % (timeArray.date().year, timeArray.date().month, timeArray.date().day)
    return strRtn


# ##############################################################################
# @param: inputDate: [int/iso/isoext]
def ToDateTime(inputDate):
    dtDate = None
    strDate = ''
    if (isinstance(inputDate, datetime.datetime) == True):
        dtDate = inputDate
    elif (isinstance(inputDate, datetime.date) == True):
        dtDate = datetime.datetime.combine(inputDate, datetime.time())
    elif (isinstance(inputDate, int) == True or isinstance(inputDate, str) == True):
        strDate = str(inputDate)
        bCheck, timeArray = isValidDate(strDate)
        if (bCheck == False or timeArray == None):
            return None
        dtDate = timeArray
    else:
        return None
    return dtDate
    '''
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
    '''

# ------------------------------------------------------------------------------
def ToDate(inputDate):
    dtDateTime = ToDateTime(inputDate)
    if (dtDateTime == None):
        return None
    return dtDateTime.date()


# @param: inputDate: [datetime.date/int/iso/isoext]
def ToIso(inputDate):
    dtRtn = ToDate(inputDate)
    if (dtRtn == None):
        return None
    strRtn = "%04d%02d%02d" % (dtRtn.year, dtRtn.month, dtRtn.day)
    return strRtn


# @param: inputDate: [datetime.date/int/iso/isoext]
def ToIsoExt(inputDate):
    dtRtn = ToDate(inputDate)
    if (dtRtn == None):
        return None
    strRtn = "%04d-%02d-%02d" % (dtRtn.year, dtRtn.month, dtRtn.day)
    return strRtn


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
        self.__nFrom = 0        # int
        self.__nTo = 0          # int
        self.__listDate = []    # list<int>

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
            return

    def IsValid(self):
        return (self.__nFrom != 0 and self.__nTo != 0)

    def From(self):
        return self.__nFrom
    def To(self):
        return self.__nTo

    # 获取日期区间内的所有日期
    def DateList(self):
        self.__GenDateList()
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
    # @param:  dpRhs: CDataPeriod
    # @return: CDatePeriod
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


    def __GenDateList(self):
        nLoopDate = self.__nFrom
        if (self.IsValid()):
            while (nLoopDate  <= self.__nTo):
                self.__listDate.append(nLoopDate)
                strLoopDate = Tomorrow(nLoopDate)
                nLoopDate = int(strLoopDate)

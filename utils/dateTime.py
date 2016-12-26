# -*- coding:utf-8 -*-
# Create On 20161221
# Auth: wang.yijian
# desc: 日期时间相关

import time
import datetime

# YYYY-MM-DD
def isValidDate_IsoExt(str):
    try:
        if (len(str) != 10):
            return False
        time.strptime(str, "%Y-%m-%d")
        return True
    except:
        return False

# YYYYMMDD
def isValidDate_Iso(str):
    '''判断是否是一个有效的日期字符串'''
    try:
        if (len(str) != 8):
            return False
        time.strptime(str, "%Y%m%d")
        return True
    except:
        return False

def DateFormat_Iso2IsoExt(strIso):
    if (isValidDate_Iso(strIso) == False):
        return None
    timeArray = time.strptime(strIso, "%Y%m%d")
    return time.strftime("%Y-%m-%d", timeArray)

def DateFormat_IsoExt2Iso(strIsoExt):
    if (isValidDate_IsoExt(strIsoExt) == False):
        return None
    timeArray = time.strptime(strIsoExt, "%Y-%m-%d")
    return time.strftime("%Y%m%d", timeArray)

def ToIso(inputDate):
    strDate = inputDate
    if (isinstance(inputDate, datetime.date)):
        strDate = inputDate.strftime('%Y%m%d')
        return strDate
    if (strDate != ''):
        if (isValidDate_IsoExt(strDate)):
            return DateFormat_IsoExt2Iso(strDate)
        elif (isValidDate_Iso(strDate)):
            return strDate
        else:
            return None
    return ''

def ToIsoExt(inputDate):
    strDate = inputDate
    if (isinstance(inputDate, datetime.date)):
        strDate = inputDate.strftime('%Y-%m-%d')
        return strDate

    if (strDate != ''):
        if (isValidDate_IsoExt(strDate)):
            return strDate
        elif (isValidDate_Iso(strDate)):
            return DateFormat_Iso2IsoExt(strDate)
        else:
            return None
    return ''

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
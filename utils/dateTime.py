# -*- coding:utf-8 -*-
# Create On 20161221
# Auth: wang.yijian
# desc: 日期时间相关

import time

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

def DateFromat_Iso2IsoExt(strIso):
    if (isValidDate_Iso(strIso) == False):
        return None
    timeArray = time.strptime(strIso, "%Y%m%d")
    return time.strftime("%Y-%m-%d", timeArray)

def DateFormat_IsoExt2Iso(strIsoExt):
    if (isValidDate_IsoExt(strIsoExt) == False):
        return None
    timeArray = time.strptime(strIsoExt, "%Y-%m-%d")
    return time.strftime("%Y%m%d", timeArray)

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

# print(DateFromat_Iso2IsoExt('20100203'))
# print(DateFormat_IsoExt2Iso('2010-02-03'))
# -*- coding:utf-8 -*-
# Create On 20161221
# Auth: wang.yijian
# desc: 日期时间相关

import time

def is_valid_date(str):
    '''判断是否是一个有效的日期字符串'''
    try:
        if (len(str) != 10):
            return False
        time.strptime(str, "%Y-%m-%d")
        return True
    except:
        return False

# print(is_valid_date('2016-12-31'))
# print(is_valid_date('2016-2-2'))
# print(is_valid_date('2016-02-29'))
# print(is_valid_date('20161231'))
# print(is_valid_date('2016-12-32'))
# print(is_valid_date('2015-02-29'))

# a = "2013-02-2 23:40:00"
# timeArray = time.strptime(a, "%Y-%m-%d %H:%M:%S")
# print(time.strftime("%Y-%m-%d %H:%M:%S", timeArray))
# -*- coding:utf-8 -*-
# Create On 20170105
# Auth: wang.yijian
# desc: 源代码定位

import inspect

def Frame(nCallerDepth = 1):
    callerframerecord = inspect.stack()[nCallerDepth]   # 0 represents this line
                                                        # 1 represents line at caller
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)
    return info

def FrameStr(nCallerDepth = 1):
    info = Frame(nCallerDepth + 1)
    strOut = 'msg: File "' + info.filename + '", line ' + str(info.lineno) + ' in function [' + info.function + ']'
    return strOut

def PrintFrame(nCallerDepth = 1):
    strInfo = FrameStr(nCallerDepth + 1)
    print(strInfo)

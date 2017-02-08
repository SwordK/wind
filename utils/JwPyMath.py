# -*- coding:utf-8 -*-
# Create On 20170208
# Auth: wang.yijian
# desc: Jason Wang's Python 数学相关

def IntDevideToList(nValue):
    """
    将整数按位保存为list。 其中 list[0] 为最高位, list[-1] 为个位
    """
    listResult = []
    while nValue:
        #divmod()是内置函数，返回整商和余数组成的元组
        nValue, r = divmod(nValue, 10)
        listResult.append(r)
    listResult.reverse()
    return listResult
# print(IntDevideToList(1234567))


def ListMergeToInt(listValue):
    """
    将list按位保存为整数。 其中 list[0] 为最高位, list[-1] 为个位
    """
    nResult = 0
    nIndex = 0
    nLen = len(listValue)
    while nIndex < len(listValue):
        nResult += listValue[nIndex] * 10 ** (nLen - nIndex - 1)
        nIndex += 1
    return int(nResult)
# print(ListMergeToInt([1,2,3,4,5,6,7]))

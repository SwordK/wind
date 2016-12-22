# -*- coding:utf-8 -*-
# Create On 20161222
# Auth: wang.yijian
# desc: 股票处理
'''
Usage:
    Stocks:
        '600000.SH'  ->  600000
        '000002.SZ'  ->  2
    Index:
        '000906.SH'  ->  906 + 1000000 == 1000906
'''

def StockWindCode2Int(strWindCode):
    listCodes = strWindCode.split('.')
    if (len(listCodes) != 2):
        return None

    nId = 0
    if (listCodes[1] == 'SH'):
        nId = int(listCodes[0])
        if (nId < 600000):
            nId += 1000000
    elif (listCodes[1] == 'SZ'):
        nId = int(listCodes[0])
    else:
        return None
    return nId

def Int2StockWindCode(nId):
    strWindCode = ''
    if (nId >= 1000000):
        strWindCode = '%06d' % (nId - 1000000) + '.SH'
    elif (nId >= 600000):
        strWindCode = str(nId) + '.SH'
    else:
        strWindCode = '%06d' % nId + '.SZ'
    return strWindCode


# print(StockWindCode2Int('600000.SH'))
# print(StockWindCode2Int('000002.SZ'))
# print(StockWindCode2Int('000906.SH'))

# print(Int2StockWindCode(1000906))
# print(Int2StockWindCode(2))
# print(Int2StockWindCode(600000))
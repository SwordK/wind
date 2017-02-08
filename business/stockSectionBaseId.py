# -*- coding:utf-8 -*-
# Create On 20170208
# Auth: wang.yijian
# desc: 股票因子ID

"""
int4个字节  范围(-2147483648~2147483647)
eg: [118802040]
    1 18 80 20 4 0
    | __ __ __ | |-->个位：0
    | |  |  |  |---->十位：总共分n组
    | |  |  |------->百位千位：调仓间隔天数, 99 表示按照[财报日]进行调仓
    | |  |---------->万位十万位: 股票池 80[800], 50[500], 30[300], 05[50], 00[全市场]
    | |------------->百万位千万位: 因子Id 
    |--------------->亿位: 行业中性。0 表示不考虑行业中性, 1 表示普通行业中性, 2 表示Ols残差中性    
"""

import sys;sys.path.append("../")
import business.stockPool as stockPool
import business.stockSection as stockSection
import business.industry as industry
import utils.JwPyMath as JwPyMath

def StockSectionDesc2BaseId(nGroupSize, nDateInterval, euSs, euSpt, euInt):
    """
    euSpt: EU_StockPoolType
    euSs:  EU_StockSection
    euInt: EU_IndustrialNeutralType
    """
    listSsNum = JwPyMath.IntDevideToList(euSs.value)
    if len(listSsNum) == 1:
        listSsNum.insert(0,0)
    listSptNum = JwPyMath.IntDevideToList(euSpt.value / 10)
    if len(listSptNum) == 1:
        listSptNum.insert(0,0)
    listDINum = JwPyMath.IntDevideToList(nDateInterval)    
    if len(listDINum) == 1:
        listDINum.insert(0,0)
    listTail = [nGroupSize, 0]
    listDesc = [euInt.value]
    listDesc.extend(listSsNum)    
    listDesc.extend(listSptNum)
    listDesc.extend(listDINum)
    listDesc.extend(listTail)
    
    return JwPyMath.ListMergeToInt(listDesc)
#print(StockSectionDesc2BaseId(4, 20, stockSection.EU_StockSection.euSs_MarketValueTotal, stockPool.EU_StockPoolType.euspt_ZZ800, industry.EU_IndustrialNeutralType.euInt_None))


def StockSectionBaseId2Desc(nBaseId):
    """
    @ return: nGroupSize, nDateInterval, euSs, euSpt, euInt
    """
    euInt = industry.EU_IndustrialNeutralType.euInt_None
    euSs = stockSection.EU_StockSection.euSs_None
    euSpt = stockPool.EU_StockPoolType.euspt_None

    listResult = JwPyMath.IntDevideToList(nBaseId)
    nLen = len(listResult)
    
    if (nLen == 9):
        euInt = industry.EU_IndustrialNeutralType(listResult[0])
    nSs = 0
    if (nLen > 7):
        nSs = JwPyMath.ListMergeToInt(listResult[-8:-6])
    else:
        nSs = listResult[-7]
    euSs = stockSection.EU_StockSection(nSs)

    euSpt = stockPool.EU_StockPoolType(JwPyMath.ListMergeToInt(listResult[-6:-4]) * 10)
    nDateInterval = JwPyMath.ListMergeToInt(listResult[-4:-2])
    nGroupSize = listResult[-2]

    return nGroupSize, nDateInterval, euSs, euSpt, euInt
    pass
# print(StockSectionBaseId2Desc(11802041))
# print(StockSectionBaseId2Desc(1802041))
# print(StockSectionBaseId2Desc(211802041))

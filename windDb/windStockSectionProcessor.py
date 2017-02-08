# -*- coding:utf-8 -*-
# Create On 20161221
# Auth: wang.yijian
# desc: wind 量化接口 数据处理

import sys;sys.path.append("../")
import getopt
import numpy as np
import pandas as pd
from pandas import DataFrame
from pandas import Series

import business.stockPool as stockPool
import business.stockSection as stockSection
import business.position_index as indexPosition
import business.tradingCalendar as tCal
import business.industry as industry
import business.mdBar as mdBar
import business.stockCn as stockCn
import windDbBusiness as windDbBusiness
import utils.dateTime as dateTime

dictDefault1stTradingDay = { \
    stockPool.EU_StockPoolType.euspt_SZ50 : 20040102 \
    , stockPool.EU_StockPoolType.euspt_HS300 : 20050408 \
    , stockPool.EU_StockPoolType.euspt_ZZ500 : 20070115 \
    , stockPool.EU_StockPoolType.euspt_ZZ800 : 20070115 \
}

# TODO: GroupBaseId
nGroupBaseId = 100000
dBaseIndexValue = 1000.0
strColPrice = 'S_DQ_ADJCLOSE'

def GetDfCols(dfPandSAll, listTradingDay, listStocks, listStrCols):
    """
    @params:    dfPandSAll: Price and Section DataFrame
                listTradingDay:
                listStocks:
                listStrCols:
    @return:    True, PandSAll [ listStrCols is Multiple Cols ] or Series[ listStrCols is Single Col ]
                False, None
    """
    listTradingDayFix = listTradingDay
    if (isinstance(listTradingDay, list) == False):
        listTradingDayFix = list([listTradingDay])
    listStocksFix = listStocks
    if (isinstance(listStocks, list) == False):
        listStocksFix = list([listStocks])
    if (len(listTradingDayFix) <= 0 or len(listStocksFix) <= 0 or len(listStrCols) <= 0):
        return False, None

    listTradingDayFixDateTime = list()
    for inputTd in listTradingDayFix:
        dtTd = dateTime.ToDateTime(inputTd)
        if (dtTd == None):
            continue
        listTradingDayFixDateTime.append(dtTd)

    df1 = dfPandSAll[listStrCols].ix[listTradingDayFixDateTime]
    listLoc = df1.index.isin(listStocksFix, level="STOCK_WINDCODE")
    dfRtn = df1.loc[listLoc]
    return True, dfRtn


def SortingGroup_Pandas(dfDailyData_St, nGroupSize, nGroupBaseId, bMore2Less = True):
    """
    @params:    dfDailyData_St: single indexed DataFrame
                nGroupSize:
                nGroupBaseId:
                More2Less:
    @return:    dict: GroupId 2 set of Stocks

    @TODO:      implement 'More2Less'
    """
    # print(type(dfDailyData_St), dfDailyData_St)
    dictRtnGroups = dict()
    nSectionSize = dfDailyData_St.index.size

    if (nGroupSize > nSectionSize):
        for nIndex in range(0,nGroupSize):
            dictRtnGroups[nIndex] = setStocks
    else:
        nRemainder = nSectionSize % nGroupSize
        nAverageSize = 0
        if (nRemainder == 0 or bMore2Less == False):
            nAverageSize = int(nSectionSize / nGroupSize)
        else:
            nAverageSize = int(nSectionSize / nGroupSize) + 1

        nLoopSize = 0
        nGroupId = nGroupBaseId

        for strStockCode in dfDailyData_St.index:
            if (nGroupId not in dictRtnGroups.keys()):
                dictRtnGroups[nGroupId] = list()
            dictRtnGroups[nGroupId].append(strStockCode)

            nLoopSize += 1
            if (nLoopSize >= nAverageSize):
                nLoopSize = 0
                if (bMore2Less == True):
                    if (nGroupId - nGroupBaseId == nRemainder - 1):
                        nAverageSize -= 1
                else:
                    if (nGroupId == nGroupSize - nRemainder - 1):
                        nAverageSize += 1
                nGroupId += 1
    return dictRtnGroups


def AdjustPosition(dfPandSAll, dictPositionSrc, listStocks, inputTradingDay, euSs, euInt = industry.EU_IndustrialNeutralType.euInt_None):
    """
    @params:    dfPandSAll: Price and Section DataFrame
    @return:    True/False, dictPosition_Df: GroupId to Stock Value DataFrame
    """
    nGroupSize = len(dictPositionSrc)
    if (nGroupSize <= 0):
        return False, "len(dictPositionSrc) <= 0"

    dtTradingDay = dateTime.ToDateTime(inputTradingDay)
    strCol = stockSection.DfColFromEuSs(euSs)
    listStrCols = list([strCol])

    # print(list([dtTradingDay]), listStocks, listStrCols)
    bSuccess, dfSections = GetDfCols(dfPandSAll, list([dtTradingDay]), listStocks, listStrCols)
    if (bSuccess == False):
        return False, "GetDfCols Failed"
    dfSorted = dfSections.sort_values(strCol, ascending = False)
    nRows = len(dfSorted)

    nBaseGroupId = sorted(dictPositionSrc.keys())[0]
    dictRtnGroups = SortingGroup_Pandas(dfSorted.ix[dtTradingDay], len(dictPositionSrc), nBaseGroupId)

    dictPosition_Df = {}
    for nGroupId in dictPositionSrc.keys():
        dFundGroup = dictPositionSrc[nGroupId].dTotalMarketValue
        nGroupStockCount = len(dictRtnGroups[nGroupId])
        if (nGroupStockCount <= 0):
            continue

        dFundStock = dFundGroup / nGroupStockCount
        dictPosition_Df[nGroupId] = DataFrame(np.array([dFundStock] * nGroupStockCount),\
                                          index=[[dtTradingDay]*nGroupStockCount, dictRtnGroups[nGroupId]],\
                                          columns=[str(nGroupId)])

        # print(dictPosition_Df[nGroupId])
        # dictPosition[nGroupId].dTotalMarketValue = dictPositionSrc[nGroupId].dTotalMarketValue

    return True, dictPosition_Df
    pass



def InitData_Common(strDbHost, strDbUserName, strDbPasswd, strDbDatabase, euSpt, euInt, nInputBeginDate, nInputEndDate):
    """
    @usage: Step1: DBReqTradingCalendar
            Step2: DBReqIndustries_ZX
            Step3: DBReqStockPool
    """
    print('DBReqTradingCalendar ...')
    windDbBusiness.DBReqTradingCalendar(strDbHost, strDbUserName, strDbPasswd, strDbDatabase)
    tcInst = tCal.CTradingCalendar()

    if (euInt != industry.EU_IndustrialNeutralType.euInt_None):
        print('DBReqIndustries_ZX ...')
        windDbBusiness.DBReqIndustries_ZX(strDbHost, strDbUserName, strDbPasswd, strDbDatabase)

    print('DBReqStockPool ...')
    # if (False == windDbBusiness.DBReqStockPool(strDbHost, strDbUserName, strDbPasswd, strDbDatabase, euSpt, nInputBeginDate, nInputEndDate)):
    if (False == windDbBusiness.DBReqStockPool_Pandas(strDbHost, strDbUserName, strDbPasswd, strDbDatabase, euSpt)):
        print('DBReqStockPool Failed ...')
        sys.exit(3)

    return None


def ProcessInterval(dfPandSAll, listSs, listTradingDays, euSpt, dictSsPositions):
    dtIntervalBegin = listTradingDays[0]
    nLoopIntervalBegin = int(dateTime.ToIso(dtIntervalBegin))

    spManager = stockPool.CStockPoolManager_Pandas()
    spInst = spManager.GetStockPool(euSpt)
    setStocks = spInst.GetStocksByTd(nLoopIntervalBegin)
    listStocksInSp = list(setStocks)
    del setStocks

    dtIntervalBegin = listTradingDays[0]

    # 计算每日价格 基于调仓日的变化率
    dictPricesPctByTd = {}  # TradingDay 2 PricePct
    dfLastPriceRecs = DataFrame()
    dfPricesInterval = DataFrame()
    for dtTradingDay in listTradingDays[1:]:
        nTd = int(dateTime.ToIso(dtTradingDay))
        setTds = set([dtIntervalBegin, dtTradingDay])
        bSuccess, dfPrices = GetDfCols(dfPandSAll, list(setTds), listStocksInSp, [strColPrice])
        if (bSuccess == False):
            continue
                
        if (dfLastPriceRecs.empty == True):
            dfLastPriceRecs = dfPrices.ix[dtIntervalBegin]
        else:
            listBegin = list(dfPrices.ix[dtIntervalBegin].index)
            listThis = list(dfPrices.ix[dtTradingDay].index)
            listComplementarySet = list(set(listBegin).difference(set(listThis)))
            if (len(listComplementarySet) > 0):
                for strStockCode in listComplementarySet:                    
                    dPrice = float(dfLastPriceRecs[strColPrice][strStockCode])
                    df1 = pd.DataFrame([dPrice], index = [[dtTradingDay],[strStockCode]], columns = [strColPrice])
                    # dfPrices[strColPrice][dtTradingDay][strStockCode] = dPrice
                    # dfPrices = 
                    # dfPrices = pd.concat([dfPrices, df1], axis = 0, join = 'outer')
                    dfPrices = dfPrices.append(df1)
                pass
            dfLastPriceRecs = dfPrices.ix[dtTradingDay]
        dfPricesInterval = dfPricesInterval.append(dfPrices)
        # if dfPricesInterval.empty == True:
        #     dfPricesInterval = dfPrices
        # else:
        #     dfPricesInterval.ix[dtTradingDay] = dfPricesInterval.ix[dtTradingDay].append(dfPrices.ix[dtTradingDay])

        dfPricesPct = dfPrices.unstack().sort_index()
        dfPricesPct = dfPricesPct.pct_change()
        dfPricesPct.ix[dtIntervalBegin] = 0
        dfPricesPct = dfPricesPct.stack()
        dictPricesPctByTd[dtTradingDay] = dfPricesPct.drop([dtIntervalBegin])
        
        
        """
        2007-01-16 00:00:00              S_DQ_ADJCLOSE
        TRADING_DAY STOCK_WINDCODE
        2007-01-16  000001.SZ            0.044169
                    000002.SZ            0.084127
        """
    
    # 计算每日指数， 保存于dictPositions_DfAll
    dictPositions_DfAll = {}
    for euSs in listSs:
        # 调仓
        bSuccess, dictPositions_Df = AdjustPosition(dfPandSAll, dictSsPositions[euSs], listStocksInSp, nLoopIntervalBegin, euSs)
        if (bSuccess == False):
            # print('AdjustPosition Falied', nBeginDateFix, euSs)
            return False, 'AdjustPosition Falied'

        dictAllPositions_DfByGroup = {}
        for nGroupId in dictPositions_Df.keys():
            dictPositions_Df[nGroupId].index.names = ['TRADING_DAY','STOCK_WINDCODE']
            dictAllPositions_DfByGroup[nGroupId] = dictPositions_Df[nGroupId].copy()

        for dtTradingDay in listTradingDays[1:]:
            for nGroupId in dictPositions_Df.keys():
                dfCopy = dictPositions_Df[nGroupId].copy()
                dfCopy.index.levels = ([[dtTradingDay],dfCopy.index.levels[1]])
                dfConcat = pd.concat([dfCopy, dictPricesPctByTd[dtTradingDay]], axis = 1, join='outer').dropna(how='any')
                dfConcat.ix[dtTradingDay][str(nGroupId)] *= (1+dfConcat.ix[dtTradingDay][strColPrice])
                del dfConcat[strColPrice]
                dictAllPositions_DfByGroup[nGroupId] = pd.concat([dictAllPositions_DfByGroup[nGroupId], dfConcat], axis = 0, join='outer').dropna(how='any')
        
        dictPositions_DfAll[euSs] = {}
        for nGroupId in sorted(dictAllPositions_DfByGroup.keys()):
            for dtTradingDay in sorted(dictAllPositions_DfByGroup[nGroupId].index.levels[0]):
                nTd = int(dateTime.ToIso(dtTradingDay))
                # 不保存调仓日指数
                if dtTradingDay == dtIntervalBegin:
                    continue
                if dtTradingDay not in dictPositions_DfAll[euSs].keys():
                    dictPositions_DfAll[euSs][dtTradingDay] = {}
                dSum = dictAllPositions_DfByGroup[nGroupId].ix[dtTradingDay][str(nGroupId)].sum()
                dictPositions_DfAll[euSs][dtTradingDay][nGroupId] = dSum
                print(dtTradingDay, nGroupId, dSum)
                
                if (nTd == 20071226):
                    list1 = []
                    for indexItem in dictAllPositions_DfByGroup[nGroupId].ix[dtTradingDay].index:
                        df1 = dfPricesInterval[strColPrice]
                        df2 = df1[dtTradingDay]
                        dPrice = df2[indexItem]
                        # dPrice = df
                        # dPrice = dfPandSAll[strColPrice].ix[dtTradingDay].ix[indexItem]
                        strValue = str(indexItem) + '|' + str(float(dictAllPositions_DfByGroup[nGroupId].ix[dtTradingDay].ix[indexItem])) + '|' + str(float(dictAllPositions_DfByGroup[nGroupId].ix[dtTradingDay].ix[indexItem] / dSum)) + '|' + str(float(dPrice))
                        
                        list1.append(strValue)

                    print(list1)
                    print("##############")

                    # print(len(dictAllPositions_DfByGroup[nGroupId].ix[dtTradingDay].index), dictAllPositions_DfByGroup[nGroupId].ix[dtTradingDay].index)
                    # print("##############")
                    # print(dictAllPositions_DfByGroup[nGroupId].ix[dtTradingDay])
                    # print("##############")
                # print(dictAllPositions_DfByGroup[nGroupId].ix[dtTradingDay].index)
    
    return True, dictPositions_DfAll


# def ProcessYearLoop(strDbHost, strDbUserName, strDbPasswd, strDbDatabase, nBeginDate, nEndDate, euSpt, listSs, nDateInterval, nGroupSize, dictSsPositions):
def ProcessYearLoop(strDbHost, strDbUserName, strDbPasswd, strDbDatabase, listTradingDays, euSpt, listSs, nDateInterval, nGroupSize, dictSsPositions):
    spManager = stockPool.CStockPoolManager_Pandas()
    spInst = spManager.GetStockPool(euSpt)
    tcInst = tCal.CTradingCalendar()

    nTdLen = len(listTradingDays)
    dtBeginDate = listTradingDays[0]
    dtEndDate = listTradingDays[-1]
    nBeginDate = int(dateTime.ToIso(dtBeginDate))
    nEndDate = int(dateTime.ToIso(dtEndDate))

    # Init Loop Md and Section Data
    setStocks = spInst.GetStocksByDatePeriod(nBeginDate, nEndDate)
    print('DBReqStockEODPrice ...')
    dfEODPrice = windDbBusiness.DBReqStockEODPrice_Pandas(strDbHost, strDbUserName, strDbPasswd, strDbDatabase, setStocks, str(nBeginDate), str(nEndDate))
    if (dfEODPrice.empty == True):
        print('!!! DBReqStockEODPrice_Pandas return Empty DataFrame !!!')

    print('DBReqStockSections_Pandas ...')
    setSst = set()
    for item in listSs:
        setSst.add(stockSection.Ss2Sst(item))
    dfSectionEOD, dfSectionFinancial = windDbBusiness.DBReqStockSections_Pandas(strDbHost, strDbUserName, strDbPasswd, strDbDatabase, setSst, setStocks, str(nBeginDate), str(nEndDate))
    del setStocks, setSst
    dfPandSAll = pd.concat([dfEODPrice, dfSectionEOD, dfSectionFinancial], axis = 1, join = 'outer')
    print(str(nBeginDate) + ' to ' + str(nEndDate) + ' Inited')
    
    dictIndexYearLoop = {}
    for euSs in listSs:
        dictIndexYearLoop[euSs] = {}
        if (dictSsPositions[euSs] == None):   # 未初始化
            if(nBeginDate == dictDefault1stTradingDay[euSpt]):   # 通过首日进行初始化
                dictSsPositions[euSs] = {}
                nGroupIndex = 0
                while nGroupIndex < nGroupSize:
                    dictSsPositions[euSs][nGroupIndex + nGroupBaseId] = indexPosition.CPosition_Index()
                    dictSsPositions[euSs][nGroupIndex + nGroupBaseId].dTotalMarketValue = dBaseIndexValue
                    nGroupIndex += 1
            else:   # 通过昨日进行初始化
                pass

    # 计算自由流通市值
    if (stockSection.EU_StockSection.euSs_MarketValueFlowingFree in listSs and dfSectionEOD.empty == False):
        strColMvFf = stockSection.DfColFromEuSs(stockSection.EU_StockSection.euSs_MarketValueFlowingFree)
        strColFreeShares = 'FREE_SHARES_TODAY'
        dfPandSAll[strColMvFf] = np.nan
        for index, row in self.dfPandSAll.iterrows():
            dfPandSAll[strColMvFf][index] = dfPandSAll[strColPrice][index] * dfPandSAll[strColFreeShares][index]
        del dfPandSAll[strColFreeShares]
    
    nLoopIntervalBegin = nBeginDate
    nLoopIndex = 0
    while True:
        # nLoopIntervalBegin 为调仓日
        ## 获取nDateInterval 个TradingDay，保存在listTradingDays_Interval中        
        nIntervalTailIndex = min((nLoopIndex+1)*nDateInterval, nTdLen) + 1
        listTradingDays_Interval = listTradingDays[nLoopIndex * nDateInterval : nIntervalTailIndex]
        print(listTradingDays_Interval)
        
        bSuccess, dictIndexInterval = ProcessInterval(dfPandSAll, listSs, listTradingDays_Interval, euSpt, dictSsPositions)
        if (bSuccess == True):
            for euSs in dictIndexYearLoop.keys():
                dictIndexYearLoop[euSs].update(dictIndexInterval[euSs])
                lastKey = sorted(dictIndexInterval[euSs].keys())[-1]
                for nGroupId in dictSsPositions[euSs].keys():
                    dictSsPositions[euSs][nGroupId].dTotalMarketValue = dictIndexInterval[euSs][lastKey][nGroupId]

        if (listTradingDays_Interval[-1] >= dtEndDate):
            break        
        nLoopIndex += 1

    return True, dictIndexYearLoop


def ProcessStockSections(strDbHost, strDbUserName, strDbPasswd, strDbDatabase, \
    nDateInterval, nGroupSize, i_strBeginDate, i_strEndDate, euSpt, listSs, euInt):
    """
    @param:     strDbHost, strDbUserName, strDbPasswd, strDbDatabase:  DataBase Info
                euSpt:  Stock Pool Type
                listSs: list[Stock Section]
                euInt:  Industrial Neutral Type
                i_strBeginDate, i_strEndDate:  [string] YYYY-MM-DD
    """
    # 修正开始日期和结束日期
    strInputBeginDate = dateTime.ToIso(i_strBeginDate)
    strInputEndDate = dateTime.ToIso(i_strEndDate)
    if (strInputBeginDate == None or strInputEndDate == None):
        print('input beginDate or endDate error: ', i_strBeginDate, i_strEndDate)
        sys.exit(3)
    nInputBeginDate = int(min(strInputBeginDate, strInputEndDate))
    nInputEndDate = int(max(strInputBeginDate, strInputEndDate))

    if (nInputBeginDate < dictDefault1stTradingDay[euSpt]):
        nInputBeginDate = dictDefault1stTradingDay[euSpt]

    # 初始化通用数据
    InitData_Common(strDbHost, strDbUserName, strDbPasswd, strDbDatabase, euSpt, euInt, nInputBeginDate, nInputEndDate)

    # 每次处理2年内的数据，处理完释放内存
    nBeginDateFix = nInputBeginDate
    nEndDateFix = nInputEndDate
    spManager = stockPool.CStockPoolManager_Pandas()
    spInst = spManager.GetStockPool(euSpt)
    tcInst = tCal.CTradingCalendar()

    dictSsPositions = {}
    dictSsDailyIndex = {}
    for euSs in listSs:
        dictSsPositions[euSs] = None
        dictSsDailyIndex[euSs] = {}

    while nBeginDateFix < nInputEndDate:
        ## 获取两年后的昨天，如果晚于nInputEndDate，则设置为nInputEndDate
        nEndDateFix = int(dateTime.TodayInNextYear(nBeginDateFix))
        nEndDateFix = int(dateTime.TodayInNextYear(nEndDateFix))
        nEndDateFix = int(dateTime.Yestoday(nEndDateFix))
        if (nEndDateFix > nInputEndDate):
            nEndDateFix = nInputEndDate

        listTradingDays = list([dateTime.ToDateTime(nBeginDateFix)])
        nDateLoop = nBeginDateFix
        while True:
            bSuccess, nDateLoop = tcInst.GetNextTradingDay('SSE', nDateLoop)
            if (bSuccess == False):
                print('GetNextTradingDay Failed')
                break
            if (nDateLoop > nEndDateFix):
                break
            listTradingDays.append(dateTime.ToDateTime(nDateLoop))
        del nDateLoop
        
        ## 修正循环日期列表，保存数量为 nDateInterval 的整数倍
        nTdLen = len(listTradingDays)
        if (nTdLen % nDateInterval != 0 and nEndDateFix != nInputEndDate):
            nTdLen_Fix = int(nTdLen / nDateInterval) * nDateInterval + 1
            listTradingDays = listTradingDays[0:nTdLen_Fix]
        dtBeginDateFix = dateTime.ToDateTime(nBeginDateFix)
        dtEndDateFix = listTradingDays[-1]
        nEndDateFix = int(dateTime.ToIso(dtEndDateFix))
        # print('from ' + str(nBeginDateFix) + ' to ' + str(nEndDateFix))        

        bSuccess, dictIndexYearLoop = ProcessYearLoop(strDbHost, strDbUserName, strDbPasswd, strDbDatabase, listTradingDays, euSpt, listSs, nDateInterval, nGroupSize, dictSsPositions)
        for euSs in dictIndexYearLoop.keys():
            dictSsDailyIndex[euSs].update(dictIndexYearLoop[euSs])
            its = sorted(dictSsDailyIndex[euSs].items())
            dictSsDailyIndex[euSs] = dict(its)
            lastKey = sorted(dictIndexYearLoop[euSs].keys())[-1]
            for nGroupId in dictSsPositions[euSs].keys():
                dictSsPositions[euSs][nGroupId].dTotalMarketValue = dictIndexYearLoop[euSs][lastKey][nGroupId]

        nBeginDateFix = nEndDateFix
    pass


def PrintUsage(strAppName):
    """
    @usage:  Print Module Usage
    @return: None
    """
    strUsage = strAppName + ' -i <dateinterval> -g <groupsize> -b <begindate> -e <enddate> -p <stockpool> -s <stocksection> -n <neutral>\n'
    strUsage += "\tDESCRIPTION \n"
    strUsage += "\t\t-i, --dateinterval\n"
    strUsage += "\t\t\t[int]    set Adjust Portfolios Date Interval\n"
    strUsage += "\t\t-g, --groupsize\n"
    strUsage += "\t\t\t[int]    set Stock Section Group Size\n"
    strUsage += "\t\t-b, --begindate\n"
    strUsage += "\t\t\t[date]   set Begin Date [yyyymmdd]\n"
    strUsage += "\t\t-e, --enddate\n"
    strUsage += "\t\t\t[date]   set End Date [yyyymmdd]\n"
    strUsage += "\t\t-p, --stockpool\n"
    strUsage += "\t\t\t[string] set Stock Pool. See More Input [-p More]\n"
    strUsage += "\t\t-s, --stocksection\n"
    strUsage += "\t\t\t[string] set Stock Section. See More Input [-s More]\n"
    strUsage += "\t\t-n, --neutral\n"
    strUsage += "\t\t\t[string] set Industrial neutral. Default is none. [none|common|ols]\n"
    print(strUsage)
    return None


def ParseOpts(strAppName, argv):
    """
    @return: dateinterval, groupsize, begindate, enddate, stockpool, stocksection, industrialneutral
    """
    try:
      opts, args = getopt.getopt(argv,"hi:g:b:e:p:s:n:",["dateinterval=","groupsize=","begindate=","enddate=","stockpool=","stocksection=","neutral="])
    except getopt.GetoptError:
        print('params error')
        PrintUsage(strAppName)
        sys.exit(2)

    if (len(opts) == 0):
        PrintUsage(strAppName)
        sys.exit(2)

    nDateInterval = 0
    nGroupSize = 0
    strBeginDate = ''
    strEndDate = ''
    strStockPool = ''
    strStockSection = ''
    strIndustrialNeutral = 'none'
    for opt, arg in opts:
        if opt == '-h':
            PrintUsage(strAppName)
            sys.exit()
        elif opt in ("-i", "--dateinterval"):
            nDateInterval = int(arg)
        elif opt in ("-g", "--groupsize"):
            nGroupSize = int(arg)
        elif opt in ("-b", "--begindate"):
            strBeginDate = arg
        elif opt in ("-e", "--enddate"):
            strEndDate = arg
        elif opt in ("-p", "--stockpool"):
            strStockPool = arg
        elif opt in ("-s", "--stocksection"):
            strStockSection = arg
        elif opt in ("-n", "--neutral"):
            strIndustrialNeutral = arg

    euSpt = stockPool.GetStockPoolByStr(strStockPool)
    if (strStockPool == 'More' or (euSpt == stockPool.EU_StockPoolType.euspt_None and strStockPool != '')):
        strSupportedSp = '-p ' + stockPool.GetSupportedSp()
        print(strSupportedSp)
        sys.exit(2)

    # euSs = stockSection.SsFromString(strStockSection)
    if (strStockSection == 'More'):
        strSupportedSs = '-p ' + stockSection.GetSupportedSs()
        print(strSupportedSs)
        sys.exit(2)

    listSplit = strStockSection.split('|')
    listSs = list()
    for strSs in listSplit:
        euSs = stockSection.SsFromString(strSs)
        if (euSs != stockSection.EU_StockSection.euSs_None):
            listSs.append(euSs)

    if (nDateInterval <= 0):
        print('-i <--dateinterval> is needed')
        PrintUsage(strAppName)
        sys.exit(2)
    if (nGroupSize <= 0):
        print('-g <--groupsize> is needed')
        PrintUsage(strAppName)
        sys.exit(2)
    if (strBeginDate == '' or strEndDate == ''):
        print('-b <--begindate> and -e <--enddate> is needed')
        PrintUsage(strAppName)
        sys.exit(2)
    if (euSpt == stockPool.EU_StockPoolType.euspt_None):
        print('-p <--stockpool> is needed')
        PrintUsage(strAppName)
        sys.exit(2)
    if (len(listSs) == 0):
        print('-s <--stocksection> is needed')
        PrintUsage(strAppName)
        sys.exit(2)
    return nDateInterval, nGroupSize, int(strBeginDate), int(strEndDate), euSpt, listSs, industry.GetIndustrialNeutralTypeByStr(strIndustrialNeutral)


def main(listArgs):
    listParams = ParseOpts(listArgs[0], listArgs[1:])
    if (len(listParams) != 7):
        print('params parse error')
        sys.exit(2)
    strDbHost = ''
    strDbUserName = ''
    strDbPasswd = ''
    strDbDatabase = ''

    strDbHost = '10.63.6.100'
    strDbUserName = 'ForOTC'
    strDbPasswd = 'otc12345678'
    strDbDatabase = 'WindDB'

    print(listParams)

    ProcessStockSections(strDbHost, strDbUserName, strDbPasswd, strDbDatabase, \
        listParams[0], listParams[1], listParams[2], listParams[3], listParams[4], listParams[5], listParams[6])

if __name__ == '__main__':
    main(sys.argv)


# -*- coding:utf-8 -*-
# Create On 20161221
# Auth: wang.yijian
# desc: wind 量化接口 数据处理

import sys;sys.path.append("../")
import getopt
import business.stockPool as stockPool
import business.stockSection as stockSection
import business.position_index as indexPosition
import business.tradingCalendar as tCal
import business.industry as industry
import business.mdBar as mdBar
import windDbBusiness
import utils.dateTime as dateTime


# @return: dictRtnGroups: groupId -> set<CStockSectionElem>
def SortingGroup(setInput, nGroupSize, nGroupBaseId, bMore2Less = True):
    if (len(setInput) == 0 or nGroupSize <= 0):
        return None
    setSortedInput = sorted(setInput)

    dictRtnGroups = {}              # groupId -> set<CStockSectionElem>
    nSetInputSize = len(setSortedInput)
    if (nGroupSize > nSetInputSize):
        for nIndex in range(0, nGroupSize):
            dictRtnGroups[nIndex + nGroupBaseId] = set()
            dictRtnGroups[nIndex + nGroupBaseId] = setSortedInput
    else:
        nRemainder = nSetInputSize % nGroupSize
        nAverageSize = 0
        if (nRemainder == 0 or bMore2Less == False):
            nAverageSize = int(nSetInputSize / nGroupSize)
        else:
            nAverageSize = int(nSetInputSize / nGroupSize) + 1

        nLoopSize = 0;
        nGroupId = nGroupBaseId
        for item in setSortedInput:
            if (nGroupId not in dictRtnGroups.keys()):
                dictRtnGroups[nGroupId] = set()
            dictRtnGroups[nGroupId].add(item)

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

# @param:  dictGroupFunds: groupid -> dFunds
#          nGroupSize:
#          dictInsts: nStockId -> CStockSectionElem
#          dtTradingDay
# @return: dictPositions: groupId -> CPositionSet_Index
def AdjustPortfolios(dictGroupFunds, nGroupSize, dictInsts, dtTradingDay):
    if (len(dictGroupFunds) == 0 or nGroupSize <= 0 or len(dictInsts) == 0):
        return None

    listGroupFundsKeys = sorted(dictGroupFunds.keys())
    nGroupBaseId = listGroupFundsKeys[0]

    setSections = set()
    for key in dictInsts.keys():
        setSections.add(dictInsts[key])
    sortedListSections = sorted(setSections)
    nTradingDay = int(dateTime.ToIso(dtTradingDay))

    dictICode2Index = {}
    for item in sortedListSections:
        strStock = item.GetStockId()
        strICode = '-'
        # 行业中性判断
        if (strICode == ''):
            continue

        if (strICode not in dictICode2Index.keys()):
            dictICode2Index[strICode] = set()
        dictICode2Index[strICode].add(item)

    # 分组
    dictGroupsByIndustry = {}       # 行业 -> 分组 -> set<股票>
    for itemICode in dictICode2Index:
        dictRtn = SortingGroup(dictICode2Index[itemICode], nGroupSize, nGroupBaseId)
        if (dictRtn != None):
            if (itemICode not in dictGroupsByIndustry.keys()):
                dictGroupsByIndustry[itemICode] = {}
            dictGroupsByIndustry[itemICode] = dictRtn

    nIndustrySize = len(dictGroupsByIndustry)
    if (nIndustrySize <= 0):
        return None

    # 调整分组并分配资金
    dictPositions = {}              # groupId -> CPositionSet_Index
    for keyGroupId in listGroupFundsKeys:
        if (keyGroupId not in dictPositions.keys()):
            dictPositions[keyGroupId] = indexPosition.CPositionSet_Index()
        dictPositions[keyGroupId].dTotalMarketValue = dictGroupFunds[keyGroupId]
        dFundAverage_Industry = dictPositions[keyGroupId].dTotalMarketValue / nIndustrySize
        for itemICode in dictGroupsByIndustry.keys():
            if (keyGroupId not in dictGroupsByIndustry[itemICode].keys()):
                print('keyGroupId not in dictGroupsByIndustry[itemICode].keys()', keyGroupId)
                continue
            if (len(dictGroupsByIndustry[itemICode][keyGroupId]) <= 0):
                print('len(dictGroupsByIndustry[itemICode][keyGroupId]) <= 0')
                continue
            dFundAverage_Stock = dFundAverage_Industry / len(dictGroupsByIndustry[itemICode][keyGroupId])
            print(len(dictGroupsByIndustry[itemICode][keyGroupId]), dFundAverage_Stock)

            for item in dictGroupsByIndustry[itemICode][keyGroupId]:
                pos = indexPosition.CPosition_Index()
                pos.dtTradingDay = nTradingDay
                pos.nStockId = item.GetStockId()
                pos.nSsId = keyGroupId
                pos.dMarketValue = dFundAverage_Stock
                dictPositions[keyGroupId].Add(pos)
                pass
    if (len(dictPositions) == 0):
        return None
    return dictPositions


def AdjustPosition(stockPoolInst, dictGroupFunds, dtTradingDay, euSs, nGroupSize, euInt = industry.EU_IndustrialNeutralType.euInt_None):
    if (nGroupSize <= 0):
        print('nGroupSize <= 0: ', nGroupSize)
        return None
    if (isinstance(stockPoolInst, stockPool.CStockPool) == False):
        print('stockPoolInst is not instance of CStockPool')
        return None
    if (isinstance(euSs, stockSection.EU_StockSection) == False):
        print('euSst is not instance of EU_StockSectionType')
        return None
    if (isinstance(euInt, industry.EU_IndustrialNeutralType) == False):
        print('euInt is not instance of EU_IndustrialNeutralType')
        return None
    listStocks = stockPoolInst.GetStocksByTd(dtTradingDay)
    if (listStocks == None or len(listStocks) <= 0):
        print('stockPoolInst.GetStocksByTd return empty')
        return None

    euSst = stockSection.Ss2Sst(euSs)
    dtSection = dateTime.ToDateTime(dtTradingDay).date()

    # 季报因子
    if (euSst == stockSection.EU_StockSectionType.euSst_Growing or euSst == stockSection.EU_StockSectionType.euSst_Quality):
        dtSection = tCal.CTradingCalendar.GetStockReportPeriod(dtTradingDay)

    # 分配因子
    dictSectionInfo = {}        # nStockId -> CStockSectionElem
    ssMgr = stockSection.CStockSectionRecordsManager()
    for nStockId in listStocks:
        dSectionValue = ssMgr.GetStockSectionValue(euSs, nStockId, dtSection)
        if (dSectionValue == None):
            continue
        ssElem = stockSection.CStockSectionElem(nStockId, dtSection, euSs, dSectionValue)
        dictSectionInfo[nStockId] = ssElem

    # dictGroupFunds = {}         # nGroupId -> dFund
    # nGroupBaseId = 0
    # for nIndex in range(nGroupBaseId, nGroupBaseId + nGroupSize):
    #     nGroupId = nIndex + 1
    #     dictGroupFunds[nGroupId] = dFundTotal / nGroupSize

    dictPositions = {}          # groupId -> CPositionSet_Index
    dictPositions = AdjustPortfolios(dictGroupFunds, nGroupSize, dictSectionInfo, dtTradingDay)
    if (dictPositions == None or len(dictPositions) <= 0):
        return None
    for key in dictPositions.keys():
        dictPositions[key].FlushMd()
        dictPositions[key].CalcPosPosition()

    return dictPositions


def InitPosition(nGroupSize, stockPoolInst, nTradingDay, euSs, euInt = industry.EU_IndustrialNeutralType.euInt_None):
    dBaseIndex = 1000.0
    dIndexMultiple = 1000000.0;
    dGroupFunds = dBaseIndex * dIndexMultiple
    nGroupBaseId = 0
    dictGroupFunds = {}
    for nGroupId in range(nGroupBaseId, nGroupBaseId + nGroupSize):
        dictGroupFunds[nGroupId] = dGroupFunds

    # stockPoolInst, dictGroupFunds, dtTradingDay, euSs, nGroupSize, dFundTotal, euInt

    return AdjustPosition(stockPoolInst, dictGroupFunds, nTradingDay, euSs, nGroupSize, euInt)


def InitData_Common(strDbHost, strDbUserName, strDbPasswd, strDbDatabase, euSpt, nInputBeginDate, nInputEndDate):
    print('DBReqTradingCalendar ...')
    windDbBusiness.DBReqTradingCalendar(strDbHost, strDbUserName, strDbPasswd, strDbDatabase)
    tcInst = tCal.CTradingCalendar()

    print('DBReqIndustries_ZX ...')
    windDbBusiness.DBReqIndustries_ZX(strDbHost, strDbUserName, strDbPasswd, strDbDatabase)

    print('DBReqStockPool ...')
    if (False == windDbBusiness.DBReqStockPool(strDbHost, strDbUserName, strDbPasswd, strDbDatabase, euSpt, nInputBeginDate, nInputEndDate)):
        print('DBReqStockPool Failed ...')
        sys.exit(3)

    pass


def ProcessStockSections(strDbHost, strDbUserName, strDbPasswd, strDbDatabase, \
    nDateInterval, nGroupSize, strBeginDate, strEndDate, euSpt, euSs, strIndustrialNeutral):
    # 日期区间设置
    rtnBeginDate = dateTime.ToIso(strBeginDate)
    rtnEndDate = dateTime.ToIso(strEndDate)
    if (rtnBeginDate == None or rtnEndDate == None):
        print('input beginDate or endDate error: ', strBeginDate, strEndDate)
        sys.exit(3)
    nInputBeginDate = int(min(rtnBeginDate, rtnEndDate))
    nInputEndDate = int(max(rtnBeginDate, rtnEndDate))
    dictDefualt1stTradingDay = { \
        stockPool.EU_StockPoolType.euspt_SZ50 : 20040102 \
        , stockPool.EU_StockPoolType.euspt_HS300 : 20050408 \
        , stockPool.EU_StockPoolType.euspt_ZZ500 : 20070115 \
        , stockPool.EU_StockPoolType.euspt_ZZ800 : 20070115 \
        }

    if (nInputBeginDate < dictDefualt1stTradingDay[euSpt]):
        nInputBeginDate = dictDefualt1stTradingDay[euSpt]
    dDefault1stTradingDay = dictDefualt1stTradingDay[euSpt]

    # 初始化通用数据
    InitData_Common(strDbHost, strDbUserName, strDbPasswd, strDbDatabase, euSpt, nInputBeginDate, nInputEndDate)

    # 获取第一个交易日
    tcInst = tCal.CTradingCalendar()
    while nInputBeginDate < nInputEndDate:
        if (tcInst.IsTradingDay('SSE', nInputBeginDate) == True):
            break
        nInputBeginDate = int(dateTime.Tomorrow(nInputBeginDate))

    # StockPoolManager 和 StockPool实例
    spManager = stockPool.CStockPoolManager()
    spInst = spManager.GetStockPool(euSpt)

    # 每次处理2年内的数据，处理完释放内存
    nBeginDateFix = nInputBeginDate
    nEndDateFix = nInputEndDate
    bInited = False
    dictPositions = {}
    nDateIndex = 0

    while nBeginDateFix <= nInputEndDate:
        nEndDateFix = int(dateTime.TodayInNextYear(nBeginDateFix))
        nEndDateFix = int(dateTime.TodayInNextYear(nEndDateFix))
        if (nEndDateFix > nInputEndDate):
            nEndDateFix = nInputEndDate
        print('From', nBeginDateFix, ' To', nEndDateFix)

        setStocks = set()
        if (bInited == False):
            setStocks = spInst.GetStocksByDatePeriod(nBeginDateFix, nEndDateFix)
        else:
            strStockPoolBeginFix = dateTime.DayeDeltaByDays(nBeginDateFix, -1*nDateInterval*2)
            print('strStockPoolBeginFix', strStockPoolBeginFix, nBeginDateFix)
            setStocks = spInst.GetStocksByDatePeriod(int(strStockPoolBeginFix), nEndDateFix)

        # print(setStocks)
        if (len(setStocks) <= 0):
            print('StockPool is Empty: ', euSpt, nBeginDateFix, nEndDateFix)
            sys.exit(3)
        print('DBReqStockEODPrice ...')
        windDbBusiness.DBReqStockEODPrice(strDbHost, strDbUserName, strDbPasswd, strDbDatabase, setStocks, str(nBeginDateFix), str(nEndDateFix))

        print('DBReqStockSections ...')
        euSst = stockSection.Ss2Sst(euSs)
        windDbBusiness.DBReqStockSections(strDbHost, strDbUserName, strDbPasswd, strDbDatabase, euSst, setStocks, str(nBeginDateFix), str(nEndDateFix))

        if (bInited == False):
            dictPositions = InitPosition(nGroupSize, spInst, nInputBeginDate, euSs)
            nDateIndex = 1
            bInited = True

        if (dictPositions == None or len(dictPositions) == 0):
            return None
        # nDateIndex += 1
        if (euSst == stockSection.EU_StockSectionType.euSst_Evaluation or euSst == stockSection.EU_StockSectionType.euSst_MarketValue):
            nDateLoop = nBeginDateFix
            if (nBeginDateFix != nInputBeginDate):
                strDateLoop = dateTime.Yestoday(nDateLoop)
                if (strDateLoop == None):
                    return None
                nDateLoop = int(strDateLoop)

            while True:
                # 取下一交易日
                print(nDateLoop)
                bRtn, nDateLoop = tcInst.GetNextTradingDay('SSE', nDateLoop)
                if (bRtn == False or nDateLoop > nEndDateFix):
                    print('Break1', bRtn, nDateLoop)
                    break
                print(nDateLoop)
                # 刷新当日价格和市值
                for key in dictPositions.keys():
                    dictPositions[key].SetPosTradingDay(nDateLoop)
                    dictPositions[key].FlushMd()
                    dictPositions[key].CalcTotalMarketValue()
                    dictPositions[key].CalcPosWeight()
                    dictPositions[key].Dump()
                    pass
                # 是否调仓
                strAdjPos = '0'
                if (nDateIndex % nDateInterval == 0):
                    strAdjPos = '1'
                    # print('nDateIndex % nDateInterval == 0', nDateIndex, nDateInterval)
                    dictGroupFunds = {}
                    for key in dictPositions:
                        dictGroupFunds[key] = dictPositions[key].GetTotalMarketValue()
                    dictPositions = AdjustPosition(spInst, dictGroupFunds, nDateLoop, euSs, nGroupSize)
                    pass
                nDateIndex += 1
                bRtn, nDayCount = tcInst.GetTradingDayCount('SSE', dDefault1stTradingDay, nDateLoop)
                if (bRtn == False):
                    print('Break2', bRtn, nDayCount)
                    break
                # dump index
                strCsvIndexValue = 'stocksectionindex.csv'
                csvfile = open(strCsvIndexValue, 'a')
                for key in dictPositions:
                    outString = str(key) + ',' + str(nDateLoop) + ',' + str(dictPositions[key].dTotalMarketValue) + ',' + str(nDayCount) + ',' + strAdjPos + '\n'
                    csvfile.write(outString)
                csvfile.close()
        elif (euSst == stockSection.EU_StockSectionType.euSst_Growing or euSst == stockSection.EU_StockSectionType.euSst_Quality):
            pass
        else:
            return None

        strRemoveBefore = dateTime.DayeDeltaByDays(nEndDateFix, -1*nDateInterval)
        ssMgr = stockSection.CStockSectionRecordsManager()
        ssMgr.RemoveBefore(int(strRemoveBefore))
        mdMgr = mdBar.CMdBarDataManager()
        mdMgr.RemoveBefore(strRemoveBefore)

        nBeginDateFix = int(dateTime.Tomorrow(nEndDateFix))



# @return: dateinterval, groupsize, begindate, enddate, stockpool, stocksection, industrialneutral
def ParseOpts(strAppName, argv):
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
    try:
      opts, args = getopt.getopt(argv,"hi:g:b:e:p:s:n:",["dateinterval=","groupsize=","begindate=","enddate=","stockpool=","stocksection=","neutral="])
    except getopt.GetoptError:
        print('params error')
        print(strUsage)
        sys.exit(2)

    if (len(opts) == 0):
        print(strUsage)
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
            print(strUsage)
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
    euSs = stockSection.SsFromString(strStockSection)
    if (strStockSection == 'More' or (euSs == stockSection.EU_StockSection.euSs_None and strStockSection != '')):
        strSupportedSs = '-p ' + stockSection.GetSupportedSs()
        print(strSupportedSs)
        sys.exit(2)

    if (nDateInterval <= 0):
        print('-i <--dateinterval> is needed')
        print(strUsage)
        sys.exit(2)
    if (nGroupSize <= 0):
        print('-g <--groupsize> is needed')
        print(strUsage)
        sys.exit(2)
    if (strBeginDate == '' or strEndDate == ''):
        print('-b <--begindate> and -e <--enddate> is needed')
        print(strUsage)
        sys.exit(2)
    if (euSpt == stockPool.EU_StockPoolType.euspt_None):
        print('-p <--stockpool> is needed')
        print(strUsage)
        sys.exit(2)
    if (euSs == stockSection.EU_StockSection.euSs_None):
        print('-s <--stocksection> is needed')
        print(strUsage)
        sys.exit(2)
    return nDateInterval, nGroupSize, strBeginDate, strEndDate, euSpt, euSs, strIndustrialNeutral


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

    ProcessStockSections(strDbHost, strDbUserName, strDbPasswd, strDbDatabase, \
        listParams[0], listParams[1], listParams[2], listParams[3], listParams[4], listParams[5], listParams[6])   

if __name__ == '__main__':
    main(sys.argv)


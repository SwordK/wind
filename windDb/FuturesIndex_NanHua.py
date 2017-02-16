# -*- coding:utf-8 -*-
# Create On 20170213
# Auth: wang.yijian
# desc: 商品指数权重_南华
#       数据基于WindDb



import sys;sys.path.append("../")
import getopt
import datetime
import pymssql
import numpy as np
import pandas as pd

import business.tradingCalendar as tCal
import windDb as windDb
import windDbBusiness as windDbBusiness

import utils.dateTime as dateTime

def GetExchange(strInstId):
    listSplit = strInstId.split('.')
    if len(listSplit) != 2:
        return ''
    if listSplit[1] == 'CZC':
        return 'CZCE'
    elif listSplit[1] == 'DCE':
        return 'DCE'
    elif listSplit[1] == 'SHF':
        return 'SHFE'
    elif listSplit[1] == 'CFE':
        return 'CFFEX'
    else:
        return ''

def InitData_Common(strDbHost, strDbUserName, strDbPasswd, strDbDatabase, strDateFrom, strDateTo):
    """
    @CF: Commodity Futures
    @return: dfCFPrice, dfCFMapping
    """
    print('InitData_Common ...')
    windDbBusiness.DBReqTradingCalendar(strDbHost, strDbUserName, strDbPasswd, strDbDatabase)
    wDb = windDb.CWindDb(strDbHost, strDbUserName, strDbPasswd, strDbDatabase)
    dfCFPrice = wDb.DBReqCommondityFuturesEODPrices(strDateFrom, strDateTo)
    dfCFMapping = wDb.DBReqCommondityFuturesContractMapping_Pandas(strDateFrom, strDateTo)
    # dfFBaseInfo = wDb.DBReqFuturesContPro()

    return dfCFPrice, dfCFMapping

def BaseIndexValue():
    return 1000.0
def IndexMulti():
    return 1000000.0

# dt1stDate = dateTime.ToDateTime('20040601')
# dtLastDate = dateTime.ToDateTime('20170213')


# tcInst = tCal.CTradingCalendar()




# dictCFIdxComponentByTd = {}


def CalcIndex(strDbHost, strDbUserName, strDbPasswd, strDbDatabase, strDateFrom, strDateTo, strCsvFile):
    # 初始化数据
    tcInst = tCal.CTradingCalendar()
    ## 资金总额，分配到不同的成分中
    dFundTotal = BaseIndexValue() * IndexMulti()

    ## 读取成分比重
    dfCFIndexWeight_NanHua = pd.read_csv(strCsvFile)
    nCFRowLen = len(dfCFIndexWeight_NanHua)
    nCFColLen = len(dfCFIndexWeight_NanHua.columns)
    nCFRowIndex = 0

    ## 行情数据；连续合约实际合约对应表
    ### 循环处理成分比重表示，第一循环从数据库读取数据
    dfCFPrice = pd.DataFrame()
    dfCFMapping = pd.DataFrame()    

    dt1stDate = None
    dtLastDate = dateTime.ToDateTime(strDateTo)

    dictDailyIndexValue = {}
    dtDailyConstituent = pd.DataFrame()
    # 每次循环做一次一次指数成分调整
    while nCFRowIndex < nCFRowLen:
        dictFundByProduct = {}  # 各个品种分配的资金
        nColIndex = 0
        dtLoopFrom = None
        dtLoopTo = None

        # 处理起始日期 和 各个品种分配的初始资金
        while nColIndex < nCFColLen:
            strCol = dfCFIndexWeight_NanHua.columns[nColIndex]
            dValue = dfCFIndexWeight_NanHua[strCol][nCFRowIndex]
            if (strCol == 'TradingDay'):
                dtLoopFrom = dateTime.ToDateTime(int(dfCFIndexWeight_NanHua[strCol][nCFRowIndex]))
            else:
                if dValue != 0:
                    dictFundByProduct[strCol] = dfCFIndexWeight_NanHua[strCol][nCFRowIndex] * dFundTotal
            nColIndex += 1
        
        # 查询数据库， 初始化数据
        if (nCFRowIndex == 0):
            dt1stDate = dtLoopFrom
            dfCFPrice, dfCFMapping = InitData_Common(strDbHost, strDbUserName, strDbPasswd, strDbDatabase, dateTime.ToIso(dt1stDate), strDateTo)
        
        # 处理结束日期
        if nCFRowIndex + 1 == nCFRowLen:
            dtLoopTo = dtLastDate
        else:
            dtLoopTo = dateTime.ToDateTime(int(dfCFIndexWeight_NanHua['TradingDay'][nCFRowIndex+1]))

        if tcInst.IsTradingDay('SHFE', dateTime.ToIso(dtLoopFrom)) == False:
            bSuccess, nRtn = tcInst.GetNextTradingDay('SHFE', dtLoopFrom)
            if bSuccess == True:
                dtLoopFrom = dateTime.ToDateTime(nRtn)
            else:
                print('tcInst.GetNextTradingDay failed', 'SHFE', dtLoopFrom)
                break
        if tcInst.IsTradingDay('SHFE', dateTime.ToIso(dtLoopTo)) == False:
            bSuccess, nRtn = tcInst.GetNextTradingDay('SHFE', dtLoopTo)
            if bSuccess == True:
                dtLoopTo = dateTime.ToDateTime(nRtn)
            else:
                print('tcInst.GetNextTradingDay failed', 'SHFE', dtLoopTo)
                break
        
        print('--------------------------------------------------------------------')
        print('Processing From ' + dateTime.ToIso(dtLoopFrom) + ' To ' + dateTime.ToIso(dtLoopTo))

        # 处理每个成分
        dfLoopAll = pd.DataFrame()
        for strProduct in dictFundByProduct.keys():
            # 连续合约与现实合约进行对应
            for idxProd in dfCFMapping.ix[strProduct].index:
                # 期货合约
                strInstrument = dfCFMapping['FS_MAPPING_WINDCODE'][strProduct][idxProd]
                if strInstrument not in dfCFPrice.index.levels[0]:
                    continue
                strExchange = GetExchange(strProduct)
                if strExchange == '':
                    print('xxxxxx Exchange Is NULL: ', strProduct)
                    continue

                # 日期处理, 只处理本次循环的
                bIncludeTailRow = True
                dtProductFrom = idxProd[0]
                dtProductTo = idxProd[1]
                if dtProductFrom > dtLoopTo:
                    break
                if dtProductTo < dtLoopFrom:
                    continue
                if dtProductFrom < dtLoopFrom:
                    dtProductFrom = dtLoopFrom
                if dtProductTo >= dtLoopTo:
                    dtProductTo = dtLoopTo
                else:
                    bSuccess, nProductTo = tcInst.GetNextTradingDay(strExchange, dtProductTo)
                    if bSuccess == False:
                        continue
                    dtProductTo = dateTime.ToDateTime(nProductTo)
                    bIncludeTailRow = False

                # 获取时间区间的行情数据
                listDates = tcInst.GetTradingDayList(strExchange, dtProductFrom, dtProductTo, True)                
                dfLoopMd = dfCFPrice.ix[strInstrument].ix[listDates].dropna()
                # 处理缺失的行情数据，使用昨收盘和昨结算
                if len(list(set(listDates).difference(dfLoopMd.index))) >= 1:
                    dateLastTd = None
                    for keyDate in listDates:
                        if keyDate not in dfLoopMd.index:
                            if dateLastTd == None:
                                bSuccess, nLastTd = tcInst.GetPreTradingDay(strExchange, keyDate)
                                if (bSuccess == None):
                                    print('xxxxxx Last TradingDay Md Is NULL: ' + strInstrument + ' ' + str(keyDate))
                                    continue
                                dateLastTd = dateTime.ToDateTime(nLastTd)

                            dClose = dfLoopMd['S_DQ_CLOSE'][dateLastTd]
                            dSettle = dfLoopMd['S_DQ_SETTLE'][dateLastTd]
                            dfToday = pd.DataFrame({'S_DQ_CLOSE':[dClose], 'S_DQ_SETTLE':[dSettle]}, index=[keyDate])
                            dfToday.index.names = ['TRADE_DT']
                            dfLoopMd = pd.concat([dfLoopMd, dfToday], axis=0, join='outer')
                        dateLastTd = keyDate

                dfLoopMd['InstrumentId'] = strInstrument
                dfLoopMd['DominantContract'] = strProduct
                dfLoopMd['Volume'] = np.nan
                dfLoopMd['Value'] = np.nan
                dfLoopMd.reset_index(inplace=True)
                dfLoopMd = dfLoopMd.set_index(['DominantContract','TRADE_DT'])

                dPrice = dfLoopMd['S_DQ_CLOSE'][strProduct][dtProductFrom]
                dVolume = dictFundByProduct[strProduct] / dPrice
                dfLoopMd['Volume'][strProduct][dtProductFrom:dtProductTo] = dVolume
                dfLoopMd['Value'][strProduct][dtProductFrom:dtProductTo] = \
                    dfLoopMd['S_DQ_CLOSE'][strProduct][dtProductFrom:dtProductTo] * \
                    dfLoopMd['Volume'][strProduct][dtProductFrom:dtProductTo]

                dfLoopMd['Value'][strProduct][dtProductFrom] = dictFundByProduct[strProduct]
                # print('----------------------------')
                # print(strProduct, dtProductTo)
                # print(dfLoopMd['Value'][strProduct])
                dictFundByProduct[strProduct] = dfLoopMd['Value'][strProduct][dtProductTo]

                if bIncludeTailRow == True:
                    dfLoopAll = pd.concat([dfLoopAll, dfLoopMd], axis=0, join='outer')
                else:
                    dfLoopAll = pd.concat([dfLoopAll, dfLoopMd[:-1]], axis=0, join='outer')

        dfSwap = dfLoopAll.swaplevel(0,1)
        dfSwap['Weight'] = np.nan
        for dtKey in dfSwap['Value'].index.levels[0]:            
            total = dfSwap['Value'][dtKey].sum()
            dictDailyIndexValue[dtKey] = total
            print(str(dtKey) + ' ' + str(dfSwap['Value'][dtKey].sum()))
            dfSwap['Weight'][dtKey] = dfSwap['Value'][dtKey] / total
        nCFRowIndex += 1
        dtDailyConstituent = pd.concat([dtDailyConstituent, dfSwap], axis=0, join='outer')    
    
    
    # 处理每日每个品种的权重    
    dtDailyConstituent = dtDailyConstituent.swaplevel(0, 1)
    print('Dump Index Value into index_daily.csv')
    fIndex = open('index_daily.csv', 'w')
    for key in sorted(dictDailyIndexValue.keys()):
        strOutput = dateTime.ToIso(key) + ',' + str(dictDailyIndexValue[key] / IndexMulti()) + '\n'
        fIndex.write(strOutput)
    fIndex.close()

    del dtDailyConstituent['Volume']
    del dtDailyConstituent['Value']    

    print('Dump Index Daily Constituent into index_daily_constituent.csv')
    dtDailyConstituent.to_csv('index_daily_constituent.csv')
    
def Usage(strAppName):
    """
    """
    strUsage = strAppName + '-b <begindate> -e <enddate> -f <csvfile> \n'
    strUsage += "  DESCRIPTION \n"
    strUsage += "    -b, --begindate\n"
    strUsage += "      [date]   set Begin Date [yyyymmdd]\n"
    strUsage += "    -e, --enddate\n"
    strUsage += "      [date]   set End Date [yyyymmdd]\n"
    strUsage += "    -f, --csvfilename\n"
    strUsage += "      [string] csv file name\n"
    
    return strUsage


def ParseOpts(strAppName, argv):
    """
    @return: begindate, enddate, csvFileName
    """
    try:
      opts, args = getopt.getopt(argv,"hb:e:f:",["begindate=","enddate=","csvfilename="])
    except getopt.GetoptError:
        print('params error')
        print(Usage(strAppName))
        sys.exit(2)

    if (len(opts) == 0):
        print(Usage(strAppName))
        sys.exit(2)

    strBeginDate = ''
    strEndDate = ''
    strCsvFileName = ''
    for opt, arg in opts:
        if opt == '-h':
            Print(Usage(strAppName))
            sys.exit()        
        elif opt in ("-b", "--begindate"):
            strBeginDate = arg
        elif opt in ("-e", "--enddate"):
            strEndDate = arg
        elif opt in ("-f", "--csvfilename"):
            strCsvFileName = arg        

    return strBeginDate, strEndDate, strCsvFileName

# "CommondityFuturesIndexWeight_NanHua.csv"
def main(listArgs):
    listParams = ParseOpts(listArgs[0], listArgs[1:])
    if (len(listParams) != 3):
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

    CalcIndex(strDbHost, strDbUserName, strDbPasswd, strDbDatabase, listParams[0], listParams[1], listParams[2])

if __name__ == '__main__':
    main(sys.argv)

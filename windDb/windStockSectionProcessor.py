# -*- coding:utf-8 -*-
# Create On 20161221
# Auth: wang.yijian
# desc: wind 量化接口 数据处理

import sys;sys.path.append("../")
import getopt
import business.tradingCalendar as tc
import business.stockPool as stockPool
import business.stockSection as stockSection
import windDbBusiness


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

def AdjustPosition(stockPoolInst, dtTradingDay, euSst, dFundTotal):
    if (isinstance(stockPoolInst, stockPool.CStockPool) == False):
        print('stockPoolInst is not instance of CStockPool')
        return False




def ProcessStockSections(strDbHost, strDbUserName, strDbPasswd, strDbDatabase, \
    nDateInterval, nGroupSize, strBeginDate, strEndDate, euSpt, euSs, strIndustrialNeutral):

    print('DBReqTradingCalendar ...')
    windDbBusiness.DBReqTradingCalendar(strDbHost, strDbUserName, strDbPasswd, strDbDatabase)
    tcInst = tc.CTradingCalendar()

    print('DBReqIndustries_ZX ...')
    windDbBusiness.DBReqIndustries_ZX(strDbHost, strDbUserName, strDbPasswd, strDbDatabase)

    print('DBReqStockPool ...')
    if (False == windDbBusiness.DBReqStockPool(strDbHost, strDbUserName, strDbPasswd, strDbDatabase, euSpt)):
        print('DBReqStockPool Failed ...')
        sys.exit(3)

    spManager = stockPool.CStockPoolManager()
    spInst = spManager.GetStockPool(euSpt)
    setStocks = spInst.GetStocksByDatePeriod(strBeginDate, strEndDate)

    print('DBReqStockEODPrice ...')
    windDbBusiness.DBReqStockEODPrice(strDbHost, strDbUserName, strDbPasswd, strDbDatabase, setStocks, strBeginDate, strEndDate)

    print('DBReqStockSections ...')
    euSst = stockSection.Ss2Sst(euSs)
    windDbBusiness.DBReqStockSections(strDbHost, strDbUserName, strDbPasswd, strDbDatabase, euSst, setStocks, strBeginDate, strEndDate)

    pass



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



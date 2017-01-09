# -*- coding:utf-8 -*-
# Create On 20161222
# Auth: wang.yijian
# desc: wind 数据库 业务处理

import sys;sys.path.append("../")

import datetime

import business.tradingCalendar as tc
import business.stockPool as stockPool
import business.industry as industry
import business.mdBar as mdBar
import business.stockSection as stockSection
import utils.dateTime as dateTime
import windDb

# DBReqTradingCalendar {
def DBReqTradingCalendar(strHost, strUser, strPwd, strDb):
    dbInst = windDb.CWindDb(strHost, strUser, strPwd, strDb)
    tcInst = tc.CTradingCalendar()

    strExchange = 'SSE'
    setRtn = dbInst.DBReqTradingCalendar(strExchange)
    if (setRtn != None and len(setRtn) > 0):
        tcInst.Add(strExchange, setRtn)

    strExchange = 'SZSE'
    setRtn = dbInst.DBReqTradingCalendar(strExchange)
    if (setRtn != None and len(setRtn) > 0):
        tcInst.Add(strExchange, setRtn)

    strExchange = 'CFFEX'
    setRtn = dbInst.DBReqTradingCalendar(strExchange)
    if (setRtn != None and len(setRtn) > 0):
        tcInst.Add(strExchange, setRtn)

    strExchange = 'SHFE'
    setRtn = dbInst.DBReqTradingCalendar(strExchange)
    if (setRtn != None and len(setRtn) > 0):
        tcInst.Add(strExchange, setRtn)

    strExchange = 'DCE'
    setRtn = dbInst.DBReqTradingCalendar(strExchange)
    if (setRtn != None and len(setRtn) > 0):
        tcInst.Add(strExchange, setRtn)

    strExchange = 'CZCE'
    setRtn = dbInst.DBReqTradingCalendar(strExchange)
    if (setRtn != None and len(setRtn) > 0):
        tcInst.Add(strExchange, setRtn)
# } end of DBReqTradingCalendar


# DbReqStockPool {
def DBReqStockPool(strHost, strUser, strPwd, strDb, euSpt, nInputBeginDate = 0, nInputEndDate = 0):
    if (isinstance(nInputBeginDate, int) == False or isinstance(nInputEndDate, int) == False):
        print('nInputBeginDate and nInputEndDate must be [int]')
        return False
    strWindCode = stockPool.GetStockPoolWindCode(euSpt)
    if (strWindCode == 'None'):
        return False

    dbInst = windDb.CWindDb(strHost, strUser, strPwd, strDb)
    listStockPool = dbInst.DBReqStockPool(strWindCode)

    spManager = stockPool.CStockPoolManager()
    spInst = stockPool.CStockPool(euSpt)
    for rowElem in listStockPool:
        if (len(rowElem) != 4):
            continue
        nInDate = rowElem[1]
        nOutDate = rowElem[2]
        if (nInputEndDate != 0 and nInDate > nInputEndDate):
            continue
        if (nInputBeginDate != 0 and nOutDate < nInputBeginDate):
            continue
        elem = stockPool.CStockPoolElem(rowElem[0], int(rowElem[1]), int(rowElem[2]), int(rowElem[3]))
        spInst.AddElem(elem)

    spInst.GenerateTdIndex()
    if (False == spManager.SetStockPool(spInst)):
        return False
    return True
# } end of DBReqStockPool

# DBReqIndustries_ZX {
def DBReqIndustries_ZX(strHost, strUser, strPwd, strDb):
    dbInst = windDb.CWindDb(strHost, strUser, strPwd, strDb)
    listStockPool = dbInst.DBReqIndustries_ZX()

    ibiManager = industry.CIndustryBaseInfoManager()
    for row in listStockPool:
        if (len(row) != 6):
            continue
        industryInst = industry.CIndustryBaseInfo(row[0], row[1], row[4], int(row[2]), int(row[3]))
        ibiManager.Add(industryInst)
# } end of DBReqIndustries_ZX

# DBReqStockIndustries_ZX {
def DBReqStockIndustries_ZX(strHost, strUser, strPwd, strDb, strDateFrom = '', strDateTo = ''):
    dbInst = windDb.CWindDb(strHost, strUser, strPwd, strDb)
    listStockIndustries = dbInst.DBReqStockIndustries_ZX()

    sipManager = industry.CStockIndustryPeriodManager()
    for row in listStockIndustries:
        if (len(row) != 5):
            continue
        sipManager.AddPeriod(row[0], row[1], row[2], row[3])

    sipManager.GenerateTdIndex(strDateFrom, strDateTo)
    # sipManager.Print____dictSipL1ByTd1()
    # sipManager.Print__dictSipL1()
    # print("******************************************")
    # sipManager.Print__dictSipL1BySid()
# } end of DBReqStockIndustries_ZX

# DBReqStockEODPrice {
def DBReqStockEODPrice(strHost, strUser, strPwd, strDb, listStocks, strDateFrom = '', strDateTo = ''):
    dbInst = windDb.CWindDb(strHost, strUser, strPwd, strDb)
    listStockEODPrice = dbInst.DBReqStockEODPrice(listStocks, strDateFrom, strDateTo)
    # print('DBReqStockEODPrice() return [', len(listStockEODPrice), '] records')

    mdbarMgr = mdBar.CMdBarDataManager()
    for row in listStockEODPrice:
        if (len(row) != 9):
            continue
        # print(row)
        dtTd = dateTime.ToDateTime(row[1])
        if (dtTd == None):
            print('DBReqStockEODPrice.tradingDay error: ', row)
        mdbarData = mdBar.CMdBarData(mdBar.EU_MdBarInterval.mdbi_1d, float(row[2]), float(row[3]), float(row[4]), float(row[5]), float(row[6]), float(row[7]), float(row[8]), dtTd)
        mdbarMgr.Add(row[0], mdbarData)
    # mdbarMgr.Print()
    return True
# } end of DBReqStockEODPrice

# DBReqStockSections {
def DBReqStockSections(strHost, strUser, strPwd, strDb, euSst, listStocks, strDateFrom = '', strDateTo = ''):
    dbInst = windDb.CWindDb(strHost, strUser, strPwd, strDb)
    listStockSection = dbInst.DBReqStockSections(euSst, listStocks, strDateFrom, strDateTo)
    # print('DBReqStockSections() return [', len(listStockSection), '] records')

    ssMgr = stockSection.CStockSectionRecordsManager()
    for row in listStockSection:
        # print(row)
        if (euSst == stockSection.EU_StockSectionType.euSst_Evaluation or euSst == stockSection.EU_StockSectionType.euSst_MarketValue):
            if (len(row) == 9):
                dPe = None
                dPb = None
                dPcf = None
                dPs = None
                d_val_mv = None
                d_dq_mv = None
                d_freeshared_today = None
                if (row[2] != None):
                    dPe = float(row[2])
                if (row[3] != None):
                    dPb = float(row[3])
                if (row[4] != None):
                    dPcf = float(row[4])
                if (row[5] != None):
                    dPs = float(row[5])
                if (row[6] != None):
                    d_val_mv = float(row[6])
                if (row[7] != None):
                    d_dq_mv = float(row[7])
                if (row[8] != None):
                    d_freeshared_today = float(row[8])
                ssMgr.AddValue1(row[0], int(row[1]), dPe, dPb, dPcf, dPs, d_val_mv, d_dq_mv, d_freeshared_today)
        elif (euSst == stockSection.EU_StockSectionType.euSst_Growing or euSst == stockSection.EU_StockSectionType.euSst_Quality):
            if (len(row) == 7):
                d_qfa_yoynetprofit = None
                d_qfa_yoysales = None
                d_fa_yoy_equity = None
                d_fa_yoyroe = None
                d_fa_yoyocf = None
                if (row[2] != None):
                    d_qfa_yoynetprofit = float(row[2])
                if (row[3] != None):
                    d_qfa_yoysales = float(row[3])
                if (row[4] != None):
                    d_fa_yoy_equity = float(row[4])
                if (row[5] != None):
                    d_fa_yoyroe = float(row[5])
                if (row[6] != None):
                    d_fa_yoyocf = float(row[6])
                ssMgr.AddValue2(row[0], int(row[1]), d_qfa_yoynetprofit, d_qfa_yoysales, d_fa_yoy_equity, d_fa_yoyroe, d_fa_yoyocf)
    # ssMgr.Print()
    return True
# } end of DBReqStockSections

#listStocks = ['603883.SH' , '603885.SH' ,'603899.SH','603993.SH']
# DBReqStockSections('10.63.6.100','ForOTC','otc12345678','WindDB', stockSection.EU_StockSectionType.euSst_Evaluation, listStocks, '20160101', '20161231')
# -*- coding:utf-8 -*-
# Create On 20161222
# Auth: wang.yijian
# desc: wind 数据库

import sys;sys.path.append("../")
import datetime
import pymssql
import numpy as np
import pandas as pd
from pandas import DataFrame
import business.stockSection as stockSection
import business.stockCn as stockCn
import database.sqlServer as sqlServer
import utils.dateTime as dateTime


class CWindDb(object):
    def __init__(self,host,user,pwd,db):
        self.__strHost = host
        self.__strUser = user
        self.__strPwd = pwd
        self.__strDB = db

    def __GenSelectLimit(self, listStocks, strDateFrom = '', strDateTo = '', strStockCol = 'S_INFO_WINDCODE', strTradingDayCol = 'TRADE_DT', strTablePrefix = ''):
        strStockLimit = ''
        if (len(listStocks) > 0):
            strStockLimit = self.__GetStockLimit(listStocks, strStockCol)
        strDateLimit = ''
        if (strDateFrom != '' and strDateTo != ''):
            strDateLimit = self.__GetDateLimit(strDateFrom, strDateTo, strTradingDayCol)
        strWhereLimit = ''
        if (strStockLimit != '' or strDateLimit != ''):
            strWhereLimit = ' WHERE '
            bNeedAnd = False
            if (strStockLimit != ''):
                strWhereLimit += '(' + strStockLimit + ')'
                bNeedAnd = True
            if (strDateLimit != ''):
                if (bNeedAnd == True):
                    strWhereLimit += 'AND'
                strWhereLimit += '(' + strDateLimit + ')'
        return strWhereLimit

    def __GetDateLimit(self, strDateFrom, strDateTo, strTableCol, strTablePrefix = ''):
        if (strDateFrom == '' or strDateTo == '' or strTableCol == ''):
            return None

        strDateFromFix = dateTime.ToIso(strDateFrom)
        strDateToFix = dateTime.ToIso(strDateTo)

        if (strDateFromFix > strDateToFix):
            strDateFromFix = dateTime.ToIso(strDateTo)
            strDateToFix = dateTime.ToIso(strDateFrom)
        strRtn = '('
        strRtn += strTablePrefix + strTableCol + " >= '" + strDateFromFix
        strRtn += "') AND ("
        strRtn += strTablePrefix + strTableCol + " <= '" + strDateToFix + "')"
        return strRtn


    def __GetStockLimit(self, listStocks, strTableCol, strTablePrefix = ''):
        if (len(listStocks) == 0 or strTableCol == ''):
            return ''
        strRtn = ''
        for nStockId in listStocks:
            strStockWindCode = nStockId
            if (isinstance(nStockId, int) == True):
                strStockWindCode = stockCn.Int2StockWindCode(nStockId)
                if (strStockWindCode == None):
                    print('stockCn.Int2StockWindCode return None: ', nStockId)
                    continue
            strRtn += strTablePrefix + strTableCol + " = '" + strStockWindCode + "' OR "
        if (len(strRtn) > 4):
            strRtn = strRtn[0:-4]
        return strRtn


    # Return None or set<int>
    def DBReqTradingCalendar(self, strExchange, strStartDate = '', strEndDate = ''):
        if (strExchange == ''):
            return None
        listFuturesExchange = ['CFFEX', 'SHFE', 'DCE', 'CZCE']
        listStockExchange = ['SSE', 'SZSE']
        strStartDateFix = dateTime.ToIsoExt(strStartDate)
        strEndDateFix = dateTime.ToIsoExt(strEndDate)

        # Gen Select Sql Script
        strSelect = ""
        if (strExchange in listFuturesExchange):
            strSelect = "select TRADE_DAYS from [WindDB].[dbo].[CFUTURESCALENDAR]"
        elif (strExchange in listStockExchange):
            strSelect = "select TRADE_DAYS from [WindDB].[dbo].[ASHARECALENDAR]"
        else:
            return None
        strSelect += " where S_INFO_EXCHMARKET = '" + strExchange + "'"
        # Date Limitint Condition
        if (strStartDateFix != None and strEndDateFix != None):
            strSelect += "and (TRADE_DAYS >= '" + strStartDateFix
            strSelect += "' and TRADE_DAYS <= '" + strEndDateFix + "')"

        # Query
        sqlS = sqlServer.CSqlServer(self.__strHost, self.__strUser, self.__strPwd, self.__strDB)
        listResult = sqlS.ExecQuery(strSelect)

        setTradingCalendar = set()
        for td in listResult:
            setTradingCalendar.add(int(td[0]))
        return setTradingCalendar


    def DBReqStockPool(self, strWindCode):
        if (len(strWindCode) != 9):
            return None

        strSelect = "SELECT S_CON_WINDCODE, S_CON_INDATE, S_CON_OUTDATE, CUR_SIGN FROM [WindDB].[dbo].[AINDEXMEMBERS]"
        strSelect += " where S_INFO_WINDCODE = '" + strWindCode + "'"

        sqlS = sqlServer.CSqlServer(self.__strHost, self.__strUser, self.__strPwd, self.__strDB)
        listResult = sqlS.ExecQuery(strSelect)

        # print(listResult)
        listStockPool = []
        for row in listResult:
            if (len(row) != 4):
                continue
            strStockWindCode = row[0]
            nStockId = stockCn.StockWindCode2Int(strStockWindCode)
            if (nStockId == None):
                print('stockCn.StockWindCode2Int return None: ', strStockWindCode)
                continue

            nInDate = int(dateTime.ToIso(row[1]))
            nOutDate = -1
            nIsIn = int(row[3])
            if (nIsIn == 0):
                nOutDate = int(dateTime.ToIso(row[2]))
            else:
                dtToday = datetime.date.today()
                nOutDate = int(dateTime.ToIso(dtToday))
            listRow = [nStockId, nInDate, nOutDate, nIsIn]
            listStockPool.append(listRow)
        return listStockPool


    def DBReqIndustries_ZX(self):
        strSelect = "SELECT INDUSTRIESCODE, INDUSTRIESNAME, LEVELNUM, USED, INDUSTRIESALIAS, SEQUENCE FROM [WindDB].[dbo].[ASHAREINDUSTRIESCODE]"
        strSelect += " where INDUSTRIESCODE like 'b1%' order by 3"

        sqlS = sqlServer.CSqlServer(self.__strHost, self.__strUser, self.__strPwd, self.__strDB)
        listResult = sqlS.ExecQuery(strSelect)
        return listResult


    def DBReqStockIndustries_ZX(self):
        strSelect = "SELECT S_INFO_WINDCODE, CITICS_IND_CODE, ENTRY_DT, REMOVE_DT, CUR_SIGN FROM [WindDB].[dbo].[ASHAREINDUSTRIESCLASSCITICS];"
        sqlS = sqlServer.CSqlServer(self.__strHost, self.__strUser, self.__strPwd, self.__strDB)
        listResult = sqlS.ExecQuery(strSelect)

        listStockIndustries = []
        for row in listResult:
            if (len(row) != 5):
                continue
            strStockWindCode = row[0]
            strICode = row[1]
            nInDate = int(dateTime.ToIso(row[2]))
            nOutDate = -1
            nIsIn = int(row[4])

            if (nIsIn == 0):
                nOutDate = int(dateTime.ToIso(row[3]))
            else:
                dtToday = datetime.date.today()
                nOutDate = int(dateTime.ToIso(dtToday))
            listRow = [strStockWindCode, strICode, nInDate, nOutDate, nIsIn]
            listStockIndustries.append(listRow)
        return listStockIndustries


    def DBReqStockEODPrice(self, listStocks, strDateFrom = '', strDateTo = ''):
        strSelect = "SELECT S_INFO_WINDCODE,TRADE_DT,S_DQ_ADJOPEN,S_DQ_ADJHIGH,S_DQ_ADJLOW,S_DQ_ADJCLOSE,S_DQ_ADJPRECLOSE,S_DQ_VOLUME,S_DQ_AMOUNT FROM [WindDB].[dbo].[ASHAREEODPRICES]"
        strStockLimit = ''
        if (len(listStocks) > 0):
            strStockLimit = self.__GetStockLimit(listStocks, 'S_INFO_WINDCODE')
        strDateLimit = ''
        if (strDateFrom != '' and strDateTo != ''):
            strDateLimit = self.__GetDateLimit(strDateFrom, strDateTo, 'TRADE_DT')
        strWhereLimit = ''
        # print(strDateLimit)
        # print(strStockLimit)
        if (strStockLimit != '' or strDateLimit != ''):
            strWhereLimit = ' WHERE '
            bNeedAnd = False
            if (strStockLimit != ''):
                strWhereLimit += '(' + strStockLimit + ')'
                bNeedAnd = True
            if (strDateLimit != ''):
                if (bNeedAnd == True):
                    strWhereLimit += 'AND'
                strWhereLimit += '(' + strDateLimit + ')'
        strSelect += strWhereLimit
        sqlS = sqlServer.CSqlServer(self.__strHost, self.__strUser, self.__strPwd, self.__strDB)
        listResult = sqlS.ExecQuery(strSelect)
        return listResult



    def DBReqStockSections(self, euSst, listStocks, strDateFrom, strDateTo):
        if (len(listStocks) <= 0):
            return None
        strSelect = ""
        strDateLimit = ""
        strStockLimit = ""
        if (len(listStocks) > 0):
            strStockLimit = self.__GetStockLimit(listStocks, 'S_INFO_WINDCODE')

        if (euSst == stockSection.EU_StockSectionType.euSst_Evaluation or euSst == stockSection.EU_StockSectionType.euSst_MarketValue):
            strSelect = "SELECT S_INFO_WINDCODE, TRADE_DT, S_VAL_PE_TTM, S_VAL_PB_NEW, S_VAL_PCF_OCFTTM, S_VAL_PS_TTM , S_VAL_MV, S_DQ_MV, FREE_SHARES_TODAY FROM [WindDB].[dbo].[ASHAREEODDERIVATIVEINDICATOR]"
            strDateLimit = self.__GetDateLimit(strDateFrom, strDateTo, "TRADE_DT")
        elif (euSst == stockSection.EU_StockSectionType.euSst_Growing or euSst == stockSection.EU_StockSectionType.euSst_Quality):
            strSelect = "SELECT S_INFO_WINDCODE, REPORT_PERIOD, S_QFA_YOYNETPROFIT, S_QFA_YOYSALES, S_FA_YOY_EQUITY, S_FA_YOYROE, S_FA_YOYOCF FROM [WindDB].[dbo].[AShareFinancialIndicator]"
            strDateLimit = self.__GetDateLimit(strDateFrom, strDateTo, "REPORT_PERIOD")
        else:
            return None

        strSelect += " WHERE (" + strDateLimit + ") AND (" + strStockLimit + ")"

        sqlS = sqlServer.CSqlServer(self.__strHost, self.__strUser, self.__strPwd, self.__strDB)
        # print(strSelect)
        listResult = sqlS.ExecQuery(strSelect)
        return listResult


    # Pandas method ################################################################################
    def DBReqTradingCalendar_Pandas(self, setExchanges, strStartDate = '', strEndDate = ''):
        """
        @return:    mergedDf
                    mergedDf.empty
        #-------------------------
        @return format:
        EXCHANGE_ID  CFFEX  CZCE   DCE  SHFE   SSE  SZSE
        TRADING_DAYS
        #-------------------------
        @return eg:
        EXCHANGE_ID  CFFEX  CZCE   DCE  SHFE   SSE  SZSE
        TRADING_DAYS
        1990-10-12     NaN  True   NaN   NaN   NaN   NaN
        1990-10-15     NaN  True   NaN   NaN   NaN   NaN
        1990-10-16     NaN  True   NaN   NaN   NaN   NaN
        """
        mergedDf = pd.DataFrame()
        if (isinstance(setExchanges, set) == False):
            return mergedDf
        setFuturesExchange = set(['CFFEX', 'SHFE', 'DCE', 'CZCE'])
        setStockExchange = set(['SSE', 'SZSE'])
        strDateLimit = self.__GetDateLimit(strStartDate, strEndDate, 'TRADE_DAYS')

        dfFutures = pd.DataFrame()
        if (len(setExchanges & setFuturesExchange) > 0):
            strSelect = "select TRADE_DAYS as TRADING_DAYS, S_INFO_EXCHMARKET as EXCHANGE_ID from WindDB.dbo.CFUTURESCALENDAR "
            if (strDateLimit != None):
                strSelect += ' WHERE ' + strDateLimit
            conn = pymssql.connect(host=self.__strHost, user=self.__strUser, password=self.__strPwd, database=self.__strDB, charset="utf8")
            df = pd.read_sql_query(strSelect, conn, parse_dates = ['TRADING_DAYS'])
            conn.close()

            # 处理数据，保存到dfFutures中
            indexedDf = df.set_index(['EXCHANGE_ID', 'TRADING_DAYS']).sortlevel(0)
            indexedDf['X'] = True
            dfFutures = indexedDf.unstack(fill_value=np.nan).T

        dfStocks = pd.DataFrame()
        if (len(setExchanges & setStockExchange) > 0):
            strSelect = "select TRADE_DAYS as TRADING_DAYS, S_INFO_EXCHMARKET as EXCHANGE_ID from [WindDB].[dbo].[ASHARECALENDAR]"
            if (strDateLimit != None):
                strSelect += ' WHERE ' + strDateLimit
            conn = pymssql.connect(host=self.__strHost, user=self.__strUser, password=self.__strPwd, database=self.__strDB, charset="utf8")
            df = pd.read_sql_query(strSelect, conn, parse_dates = ['TRADING_DAYS'])
            conn.close()

            # 处理数据，保存到dfFutures中
            indexedDf = df.set_index(['EXCHANGE_ID', 'TRADING_DAYS']).sortlevel(0)
            indexedDf['X'] = True
            dfStocks = indexedDf.unstack(fill_value=np.nan).T

        mergedDf = pd.concat([dfFutures, dfStocks], axis = 1, join = 'outer')
        mergedDf = mergedDf.sortlevel(0)
        return mergedDf.xs('X')


    def DBReqStockPool_Pandas(self, strWindCode):
        """
        @return:    df
                    df.empty
        #-------------------------
        @return format:
                                    STOCK_WINDCODE
        IN_DATE     OUT_DATE(if CUR_SING==True: OUT_DATE==Today)
        #-------------------------
        @return eg:
                                    STOCK_WINDCODE
        IN_DATE     OUT_DATE
        2007-01-15  2016-06-08      600997.SH
                    2007-06-29      000725.SZ
        ...               ...             ...
        2016-12-12  2017-01-19      600291.SH
                    2017-01-19      603866.SH
        """
        df = DataFrame()
        if (len(strWindCode) != 9):
            return df

        strSelect = "SELECT S_CON_WINDCODE as STOCK_WINDCODE, S_CON_INDATE as IN_DATE, S_CON_OUTDATE as OUT_DATE, CUR_SIGN FROM WindDB.dbo.AINDEXMEMBERS"
        strSelect += " where S_INFO_WINDCODE = '" + strWindCode + "' order by CUR_SIGN desc, IN_DATE asc"

        conn = pymssql.connect(host=self.__strHost, user=self.__strUser, password=self.__strPwd, database=self.__strDB, charset="utf8")
        df = pd.read_sql_query(strSelect, conn, parse_dates = ['IN_DATE', 'OUT_DATE'])
        conn.close()

        dtToday = datetime.date.today()
        for index, row in df.iterrows():
            if (row['CUR_SIGN'] == 1.0):
                df['OUT_DATE'][index] = dtToday
            else:
                break
        del df['CUR_SIGN']
        df = df.set_index(['IN_DATE', 'OUT_DATE'])
        df = df.sortlevel([0,1])
        return df

    # def DBReqIndustries_ZX(self):
    #     strSelect = "SELECT INDUSTRIESCODE, INDUSTRIESNAME, LEVELNUM, USED, INDUSTRIESALIAS, SEQUENCE FROM [WindDB].[dbo].[ASHAREINDUSTRIESCODE]"
    #     strSelect += " where INDUSTRIESCODE like 'b1%' order by 3"

    #     sqlS = sqlServer.CSqlServer(self.__strHost, self.__strUser, self.__strPwd, self.__strDB)
    #     listResult = sqlS.ExecQuery(strSelect)
    #     return listResult

    def DBReqStockIndustries_ZX_Pandas(self):
        """
        @return:    df
        #-------------------------
        @return format:
                                    STOCK_WINDCODE CITICS_IND_CODE
        IN_DATE     OUT_DATE(if CUR_SING==True: OUT_DATE==Today)
        #-------------------------
        @return eg:
                                    STOCK_WINDCODE CITICS_IND_CODE
        IN_DATE     OUT_DATE
        2003-01-01  2004-04-30      000809.SZ      b10h040100
                    2004-04-30      000712.SZ      b10n010100
        ...               ...             ...
        2016-07-01  2017-01-19      601966.SH      b106040500
                    2017-01-19      300521.SZ      b10a020300
        2016-07-07  2017-01-19      002805.SZ      b106030800
        """
        strSelect = "SELECT S_INFO_WINDCODE as STOCK_WINDCODE, CITICS_IND_CODE, ENTRY_DT as IN_DATE, REMOVE_DT as OUT_DATE, CUR_SIGN FROM WindDB.dbo.ASHAREINDUSTRIESCLASSCITICS order by ENTRY_DT;"
        conn = pymssql.connect(host=self.__strHost, user=self.__strUser, password=self.__strPwd, database=self.__strDB, charset="utf8")
        df = pd.read_sql_query(strSelect, conn, parse_dates = ['IN_DATE', 'OUT_DATE'])
        conn.close()

        dtToday = datetime.date.today()
        for index, row in df.iterrows():
            if (row['CUR_SIGN'] == '1'):
                df['OUT_DATE'][index] = dtToday
        del df['CUR_SIGN']
        df = df.set_index(['IN_DATE', 'OUT_DATE'])
        df = df.sortlevel([0,1])
        return df


    def DBReqStockEODPrice_Pandas(self, listStocks, strDateFrom = '', strDateTo = ''):
        """
        @return:    dfEODPrice
                    dfEODPrice.empty
        #-------------------------
        @return format:
                    Prices
        Td  SCode
        #-------------------------
        @return eg:
                                  S_DQ_ADJOPEN  S_DQ_ADJCLOSE
        TRADING_DAY STOCK_WINDCODE
        2015-01-05  000002.SZ       1774.23     1838.34
                    600000.SH        124.19      125.67
        2015-01-06  000002.SZ       1800.12     1770.53
                    600000.SH        125.13      126.14
        ...                    ...                  ...
        """
        strSelect = "SELECT S_INFO_WINDCODE as STOCK_WINDCODE,TRADE_DT as TRADING_DAY,S_DQ_ADJOPEN,S_DQ_ADJHIGH,S_DQ_ADJLOW,S_DQ_ADJCLOSE,S_DQ_ADJPRECLOSE,S_DQ_VOLUME,S_DQ_AMOUNT FROM WindDB.dbo.ASHAREEODPRICES"
        strLimit = self.__GenSelectLimit(listStocks, strDateFrom, strDateTo)
        if (strLimit != None):
            strSelect +=  strLimit

        conn = pymssql.connect(host=self.__strHost, user=self.__strUser, password=self.__strPwd, database=self.__strDB, charset="utf8")
        df = pd.read_sql_query(strSelect, conn, parse_dates = ['TRADING_DAY'])
        conn.close()
        indexedDf = df.set_index(['TRADING_DAY', 'STOCK_WINDCODE'])
        dfEODPrice = indexedDf.sortlevel(0)
        return dfEODPrice


    def DBReqStockSections_Pandas(self, setSst, listStocks, strDateFrom, strDateTo):
        """
        @returns:   [dfEOD, dfFinancial]
                    None
        -------------------------
        @return format: similar to self.DBReqStockEODPrice_Pandas()
        -------------------------
        @return eg:     similar to self.DBReqStockEODPrice_Pandas()

        """
        dfEOD = DataFrame()
        dfFinancial = DataFrame()
        if (isinstance(setSst, set) == False or len(setSst) <= 0):
            return dfEOD, dfFinancial
        if (len(listStocks) <= 0):
            return dfEOD, dfFinancial

        strStockLimit = ""
        if (len(listStocks) > 0):
            strStockLimit = self.__GetStockLimit(listStocks, 'S_INFO_WINDCODE')

        if (stockSection.EU_StockSectionType.euSst_Evaluation in setSst or stockSection.EU_StockSectionType.euSst_MarketValue in setSst):
            strSelect = "SELECT S_INFO_WINDCODE as STOCK_WINDCODE, TRADE_DT as TRADING_DAY, S_VAL_PE_TTM, S_VAL_PB_NEW, S_VAL_PCF_OCFTTM, S_VAL_PS_TTM , S_VAL_MV, S_DQ_MV, FREE_SHARES_TODAY FROM WindDB.dbo.ASHAREEODDERIVATIVEINDICATOR"
            strDateLimit = self.__GetDateLimit(strDateFrom, strDateTo, "TRADE_DT")
            strSelect += " WHERE (" + strDateLimit + ") AND (" + strStockLimit + ")"

            conn = pymssql.connect(host=self.__strHost, user=self.__strUser, password=self.__strPwd, database=self.__strDB, charset="utf8")
            df = pd.read_sql_query(strSelect, conn, parse_dates = ['TRADING_DAY'])
            conn.close()
            indexedDf = df.set_index(['TRADING_DAY', 'STOCK_WINDCODE'])
            dfEOD = indexedDf.sortlevel(0)

        if (stockSection.EU_StockSectionType.euSst_Growing in setSst or stockSection.EU_StockSectionType.euSst_Quality in setSst):
            strSelect = "SELECT S_INFO_WINDCODE as STOCK_WINDCODE, REPORT_PERIOD as TRADING_DAY, S_QFA_YOYNETPROFIT, S_QFA_YOYSALES, S_FA_YOY_EQUITY, S_FA_YOYROE, S_FA_YOYOCF FROM WindDB.dbo.AShareFinancialIndicator"
            strDateLimit = self.__GetDateLimit(strDateFrom, strDateTo, "REPORT_PERIOD")
            strSelect += " WHERE (" + strDateLimit + ") AND (" + strStockLimit + ")"

            conn = pymssql.connect(host=self.__strHost, user=self.__strUser, password=self.__strPwd, database=self.__strDB, charset="utf8")
            df = pd.read_sql_query(strSelect, conn, parse_dates = ['TRADING_DAY'])
            conn.close()
            indexedDf = df.set_index(['TRADING_DAY', 'STOCK_WINDCODE'])
            dfFinancial = indexedDf.sortlevel(0)

        return dfEOD, dfFinancial



# wDb = CWindDb('10.63.6.100', 'ForOTC', 'otc12345678', 'WindDB')
# listStocks = ['600000.SH', '000002.SZ']
# print(wDb.DBReqStockSections(stockSection.EU_StockSectionType.euSst_Evaluation, listStocks, '20150101', '20151001'))
# print(wDb.DBReqStockSections(stockSection.EU_StockSectionType.euSst_Quality, listStocks, '20150101', '20151001'))
# listResult = wDb.DBReqStockEODPrice(listStocks, '20150101', '20151231')
# for elem in listResult:
#     print(elem)
# wDb.GetDateLimit('20150101', '20151231', 'TRADE_DT', 't1.')

# wDb = CWindDb('10.63.6.100', 'ForOTC', 'otc12345678', 'WindDB')
# listStocks = ['600000.SH', '000002.SZ']
# dfResult = wDb.DBReqStockEODPrice_Pandas(listStocks, '20150101', '20151231')
# print(dfResult)

# wDb = CWindDb('10.63.6.100', 'ForOTC', 'otc12345678', 'WindDB')
# listStocks = ['600000.SH', '000002.SZ']
# setSst = set([stockSection.EU_StockSectionType.euSst_Evaluation, stockSection.EU_StockSectionType.euSst_MarketValue, stockSection.EU_StockSectionType.euSst_Growing, stockSection.EU_StockSectionType.euSst_Quality])

# print(wDb.DBReqStockSection_Pandas(setSst, listStocks, '20160101', '20161231'))


# wDb = CWindDb('10.63.6.100', 'ForOTC', 'otc12345678', 'WindDB')
# listStocks = ['600000.SH', '000002.SZ']
# setExchange = set(['SSE', 'CFFEX'])
# mergedDf = wDb.DBReqTradingCalendar_Pandas(setExchange)

# wDb = CWindDb('10.63.6.100', 'ForOTC', 'otc12345678', 'WindDB')
# print(wDb.DBReqStockIndustries_ZX_Pandas())
# print(wDb.DBReqStockPool_Pandas( '000906.SH'))
#

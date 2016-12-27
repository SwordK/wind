﻿# -*- coding:utf-8 -*-
# Create On 20161222
# Auth: wang.yijian
# desc: wind 数据库

import sys;sys.path.append("../")
import datetime
from database import sqlServer as sqlServer
import utils.dateTime as dateTime


class CWindDb(object):
    def __init__(self,host,user,pwd,db):
        self.__strHost = host
        self.__strUser = user
        self.__strPwd = pwd
        self.__strDB = db

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
        if (strStartDateFix != '' and strEndDateFix != ''):
            strSelect += "and (TRADE_DAYS >= '" + strStartDateFix
            strSelect += "' and TRADE_DAYS <= '" + strEndDateFix + "')"

        # Query
        sqlS = sqlServer.CSqlServer(self.__strHost, self.__strUser, self.__strPwd, self.__strDB)
        listResult = sqlS.ExecQuery(strSelect)

        setTradingCalendar = set()
        for td in listResult:
            setTradingCalendar.add(int(td[0]))
        return sorted(setTradingCalendar)

    def DBReqStockPool(self, strWindCode):
        if (len(strWindCode) != 9):
            return None

        strSelect = "SELECT [S_CON_WINDCODE] , [S_CON_INDATE] , [S_CON_OUTDATE], [CUR_SIGN] FROM [WindDB].[dbo].[AINDEXMEMBERS]"
        strSelect += " where S_INFO_WINDCODE = '" + strWindCode + "'"

        sqlS = sqlServer.CSqlServer(self.__strHost, self.__strUser, self.__strPwd, self.__strDB)
        listResult = sqlS.ExecQuery(strSelect)

        # print(listResult)
        listStockPool = []
        for row in listResult:
            if (len(row) != 4):
                continue
            strStockWindCode = row[0]
            nInDate = dateTime.ToIso(row[1])
            nOutDate = -1
            nIsIn = int(row[3])
            if (nIsIn == 0):
                nOutDate = dateTime.ToIso(row[2])
            else:
                dtToday = datetime.date.today()
                nOutDate = int(dateTime.ToIso(dtToday))
            listRow = [strStockWindCode, nInDate, nOutDate, nIsIn]
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


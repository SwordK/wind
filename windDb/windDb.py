# -*- coding:utf-8 -*-
# Create On 20161222
# Auth: wang.yijian
# desc: wind 数据库

import sys;sys.path.append("../")
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
        strSelect = ''
        if (strExchange in listFuturesExchange):
            print(strExchange)
            strSelect = 'select TRADE_DAYS from [WindDB].[dbo].[CFUTURESCALENDAR]'
        elif (strExchange in listStockExchange):
            print(strExchange)
            strSelect = 'select TRADE_DAYS from [WindDB].[dbo].[ASHARECALENDAR]'
        else:
            return None
        strSelect += ' where S_INFO_EXCHMARKET = \'' + strExchange + '\''
        # Date Limitint Condition
        if (strStartDateFix != '' and strEndDateFix != ''):
            strSelect += 'and (TRADE_DAYS >= \'' + strStartDateFix
            strSelect += '\' and TRADE_DAYS <= \'' + strEndDateFix + '\')'

        # Query
        sqlS = sqlServer.CSqlServer(self.__strHost, self.__strUser, self.__strPwd, self.__strDB)
        listTradingCalendar = sqlS.ExecQuery(strSelect)

        setTradingCalendar = set()
        for td in listTradingCalendar:
            setTradingCalendar.add(int(td[0]))
        return sorted(setTradingCalendar)


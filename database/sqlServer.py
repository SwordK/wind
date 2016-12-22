# -*- coding:utf-8 -*-
# Create On 20161222
# Auth: wang.yijian
# desc: SQLServer

import pymssql

class CSqlServer(object):
    def __init__(self,host,user,pwd,db):
        self.__strHost = host
        self.__strUser = user
        self.__strPwd = pwd
        self.__strDb = db
        self.__conn = None

    def GetConnect(self):
        if (self.__strDb == None):
            raise(NameError,"没有设置数据库信息")
        self.__conn = pymssql.connect(host=self.__strHost,user=self.__strUser,password=self.__strPwd,database=self.__strDb,charset="utf8")
        cur = self.__conn.cursor()
        if not cur:
            raise(NameError,"连接数据库失败")
        else:
            return cur

    def ExecQuery(self,sql):
        cur = self.GetConnect()
        cur.execute(sql)
        resList = cur.fetchall()

        #查询完毕后必须关闭连接
        self.__conn.close()
        return resList

# strSelect = 'select S_INFO_EXCHMARKET, TRADE_DAYS from [WindDB].[dbo].[CFUTURESCALENDAR] where S_INFO_EXCHMARKET = \'CFFEX\''
# sqlS = CSqlServer('', '', '', 'WindDB')
# print(sqlS.ExecQuery(strSelect))

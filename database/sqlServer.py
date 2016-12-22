# -*- coding:utf-8 -*-
# Create On 20161222
# Auth: wang.yijian
# desc: SQLServer

import pymssql

class CSqlServer(object):
    strHost = None
    strUser = None
    strPwd = None
    strDb = None
    conn = None

    def __init__(self,host,user,pwd,db):
        self.strHost = host
        self.strUser = user
        self.strPwd = pwd
        self.strDb = db

    def GetConnect(self):
        if (self.strDb == None):
            raise(NameError,"没有设置数据库信息")
        self.conn = pymssql.connect(host=self.strHost,user=self.strUser,password=self.strPwd,database=self.strDb,charset="utf8")
        cur = self.conn.cursor()
        if not cur:
            raise(NameError,"连接数据库失败")
        else:
            return cur

    def ExecQuery(self,sql):
        cur = self.GetConnect()
        cur.execute(sql)
        resList = cur.fetchall()

        #查询完毕后必须关闭连接
        self.conn.close()
        return resList

# strSelect = 'select S_INFO_EXCHMARKET, TRADE_DAYS from [WindDB].[dbo].[CFUTURESCALENDAR] where S_INFO_EXCHMARKET = \'CFFEX\''
# sqlS = CSqlServer('', '', '', 'WindDB')
# print(sqlS.ExecQuery(strSelect))
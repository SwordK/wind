# -*- coding:utf-8 -*-
# Create On 20161222
# Auth: wang.yijian
# desc: 股票因子

import sys;sys.path.append("../")
from enum import Enum
import business.stockCn as stockCn

# Enum
class EU_StockSectionType(Enum):
    euSst_None = -1
    euSst_Evaluation = 0            # 估值类因子
    euSst_MarketValue = 1           # 市值类因子
    euSst_Growing = 2               # 成长类因子
    euSst_Quality = 3               # 质量类因子
    # euSst_StockForm = 4           # 股价类形态
    # euSst_Emotion = 5             # 情绪类因子
    # euSst_PriceIncrease = 6       # 动量类因子
    # euSst_Industries = 7          # 行业类因子

class EU_StockSection(Enum):
    euSs_None = -1
    euSs_Pe = 1
    euSs_Pb = 2
    euSs_Pcf = 3
    euSs_Ps = 4

    euSs_MarketValueTotal = 11
    euSs_MarketValueFlowing = 12
    euSs_MarketValueFlowingFree = 13

    euSs_Qfa_yoynetprofit = 21          # 归属母公司净利润增长率（季度同比）
    euSs_Qfa_yoysales = 22              # 营业收入增长率（季度同比）
    euSs_Fa_yoyroe = 23                 # 净资产收益率增长率
    euSs_Fa_yoyocf = 24                 # 现金流增长率
    euSs_Fa_yoy_equity = 25             # 净资产同比增长率

    euSs_Qfa_roe_deducted = 31          # ROE(单季度)

    @staticmethod
    def ToInt(euSs):
        return int(euSs)

def Ss2Sst(euSs):
    if (isinstance(euSs, EU_StockSection) == False):
        return EU_StockSectionType.euSst_None
    elif (euSs == EU_StockSection.euSs_Pe or euSs == EU_StockSection.euSs_Pb or \
        euSs == EU_StockSection.euSs_Pcf or euSs == EU_StockSection.euSs_Ps):
        return EU_StockSectionType.euSst_Evaluation
    elif (euSs == EU_StockSection.euSs_MarketValueTotal or euSs == EU_StockSection.euSs_MarketValueFlowing or \
        euSs == EU_StockSection.euSs_MarketValueFlowingFree):
        return EU_StockSectionType.euSst_MarketValue
    elif (euSs == EU_StockSection.euSs_Qfa_yoynetprofit or euSs == EU_StockSection.euSs_Qfa_yoysales or \
        euSs == EU_StockSection.euSs_Fa_yoyroe or euSs == EU_StockSection.euSs_Fa_yoyocf or euSs == EU_StockSection.euSs_Fa_yoy_equity):
        return EU_StockSectionType.euSst_Growing
    elif (euSs == EU_StockSection.euSs_Qfa_roe_deducted):
        return EU_StockSectionType.euSst_Quality

def GetSupportedSs():
    return 'pe|pb|pcf|ps|mv|dqmv|fdqmv|yoynetprofit|yoysales|yoyequity|yoyroe|yoyocf|roededucted'

def SsFromString(strSs):
    if (strSs == ""):
        return EU_StockSection.euSs_None;
    elif (strSs == "pe"):
        return EU_StockSection.euSs_Pe;
    elif (strSs == "pb"):
        return EU_StockSection.euSs_Pb;
    elif (strSs == "pcf"):
        return EU_StockSection.euSs_Pcf;
    elif (strSs == "ps"):
        return EU_StockSection.euSs_Ps;
    elif (strSs == "mv"):
        return EU_StockSection.euSs_MarketValueTotal;
    elif (strSs == "dqmv"):
        return EU_StockSection.euSs_MarketValueFlowing;
    elif (strSs == "fdqmv"):
        return EU_StockSection.euSs_MarketValueFlowingFree;
    elif (strSs == "yoynetprofit"):
        return EU_StockSection.euSs_Qfa_yoynetprofit;
    elif (strSs == "yoysales"):
        return EU_StockSection.euSs_Qfa_yoysales;
    elif (strSs == "yoyequity"):
        return EU_StockSection.euSs_Fa_yoy_equity;
    elif (strSs == "yoyroe"):
        return EU_StockSection.euSs_Fa_yoyroe;
    elif (strSs == "yoyocf"):
        return EU_StockSection.euSs_Fa_yoyocf;
    elif (strSs == "roededucted"):
        return EU_StockSection.euSs_Qfa_roe_deducted;
    else:
        return EU_StockSection.euSs_None;

# print(SsFromString('yoyocf').value)


class CStockSectionElem(object):
    def __init__(self, nStockId, nTradingDay, euSs, dSectionValue):
        self.__nStockId = nStockId
        self.__nTradingDay = nTradingDay
        self.__euSs = euSs
        self.__dValue = dSectionValue

    def __lt__(self, rhs):
        return self.__dValue < rhs.GetValue()
    def __eq__(self, rhs):
        return self.__dValue == rhs.GetValue() and self.__nStockId == rhs.GetStockId() and self.__nTradingDay == rhs.GetTradingDay() and self.__euSs == rhs.GetSectionId()
    def __hash__(self):
        return hash(self.__nStockId + " " + str(self.__nTradingDay) + " " + str(self.__euSs.value) + " " + str(self.__dValue))

    def GetStockId(self):
        return self.__nStockId
    def GetTradingDay(self):
        return self.__nTradingDay
    def GetSectionId(self):
        return self.__euSs
    def GetValue(self):
        return self.__dValue

# sectionElem1 = CStockSectionElem('000002.SZ', 20160101, EU_StockSection.euSs_MarketValueTotal, 2000000.0)
# sectionElem2 = CStockSectionElem('000001.SZ', 20160101, EU_StockSection.euSs_MarketValueTotal, 2030000.0)
# sectionElem3 = CStockSectionElem('000001.SZ', 20160101, EU_StockSection.euSs_MarketValueTotal, 2030000.0)

# print(sectionElem1 < sectionElem2)
# print(sectionElem2 == sectionElem3)

class CStockSectionRecord(object):
    def __init__(self):
        self.dPe = None                  # 市盈率
        self.dPb = None                  # 市净率
        self.dPcf = None                 # 市现率
        self.dPs = None                  # 市销率

        self.d_val_mv = None             # 总市值
        self.d_dq_mv = None              # 流通市值
        self.d_freefloat_mv = None      # 自由流通市值
        self.d_freeshared_today = None

        self.d_qfa_yoynetprofit = None   # 归属母公司净利润增长率（季度同比）
        self.d_qfa_yoysales = None       # 营业收入增长率（季度同比）

        self.d_fa_yoy_equity = None      # 净资产同比增长率
        self.d_fa_yoyroe = None          # 净资产收益率增长率
        self.d_fa_yoyocf = None          # 现金流增长率

        # self.d_qfa_roe_deducted = 0.0   # ROE(单季度)


class CStockSectionRecordsManager(object):
    __dictStockSectionsByTd = {}        # nTradingDay -> nStockId -> CStockSectionRecord
    # __dictStockSectionsByStock = {}     # nStockId -> nTradingDay -> CStockSectionRecord

    def __init__(self):
        pass

    def AddValue1(self, strStockWindCode, nTradingDay, dPe, dPb, dPcf, dPs, d_val_mv, d_dq_mv, d_freeshared_today):
        nStockId = stockCn.StockWindCode2Int(strStockWindCode)
        if (nStockId == None):
            return False
        if (nTradingDay not in self.__dictStockSectionsByTd.keys()):
            self.__dictStockSectionsByTd[nTradingDay] = {}
        if (nStockId not in self.__dictStockSectionsByTd[nTradingDay].keys()):
            self.__dictStockSectionsByTd[nTradingDay][nStockId] = CStockSectionRecord()

        self.__dictStockSectionsByTd[nTradingDay][nStockId].dPe = dPe
        self.__dictStockSectionsByTd[nTradingDay][nStockId].dPb = dPb
        self.__dictStockSectionsByTd[nTradingDay][nStockId].dPcf = dPcf
        self.__dictStockSectionsByTd[nTradingDay][nStockId].dPs = dPs
        self.__dictStockSectionsByTd[nTradingDay][nStockId].d_val_mv = d_val_mv
        self.__dictStockSectionsByTd[nTradingDay][nStockId].d_dq_mv = d_dq_mv
        self.__dictStockSectionsByTd[nTradingDay][nStockId].d_freeshared_today = d_freeshared_today
        # print(strStockWindCode, nTradingDay, self.__dictStockSectionsByTd[nTradingDay][nStockId].dPe \
        #     , self.__dictStockSectionsByTd[nTradingDay][nStockId].dPb \
        #     , self.__dictStockSectionsByTd[nTradingDay][nStockId].dPcf \
        #     , self.__dictStockSectionsByTd[nTradingDay][nStockId].dPs \
        #     , self.__dictStockSectionsByTd[nTradingDay][nStockId].d_val_mv \
        #     , self.__dictStockSectionsByTd[nTradingDay][nStockId].d_dq_mv \
        #     , self.__dictStockSectionsByTd[nTradingDay][nStockId].d_freeshared_today)
        return True

    def AddValue2(self, strStockWindCode, nTradingDay, d_qfa_yoynetprofit, d_qfa_yoysales, d_fa_yoy_equity, d_fa_yoyroe, d_fa_yoyocf):
        nStockId = stockCn.StockWindCode2Int(strStockWindCode)
        if (nStockId == None):
            return False
        if (nTradingDay not in self.__dictStockSectionsByTd.keys()):
            self.__dictStockSectionsByTd[nTradingDay] = {}
        if (nStockId not in self.__dictStockSectionsByTd[nTradingDay].keys()):
            self.__dictStockSectionsByTd[nTradingDay][nStockId] = CStockSectionRecord()

        self.__dictStockSectionsByTd[nTradingDay][nStockId].d_qfa_yoynetprofit = d_qfa_yoynetprofit
        self.__dictStockSectionsByTd[nTradingDay][nStockId].d_qfa_yoysales = d_qfa_yoysales
        self.__dictStockSectionsByTd[nTradingDay][nStockId].d_fa_yoy_equity = d_fa_yoy_equity
        self.__dictStockSectionsByTd[nTradingDay][nStockId].d_fa_yoyroe = d_fa_yoyroe
        self.__dictStockSectionsByTd[nTradingDay][nStockId].d_fa_yoyocf = d_fa_yoyocf
        # self.__dictStockSectionsByTd[nTradingDay][nStockId].d_qfa_roe_deducted = d_qfa_roe_deducted
        # print(strStockWindCode, nTradingDay, self.__dictStockSectionsByTd[nTradingDay][nStockId].d_qfa_yoynetprofit \
        #     , self.__dictStockSectionsByTd[nTradingDay][nStockId].d_qfa_yoysales \
        #     , self.__dictStockSectionsByTd[nTradingDay][nStockId].d_fa_yoy_equity \
        #     , self.__dictStockSectionsByTd[nTradingDay][nStockId].d_fa_yoyroe \
        #     , self.__dictStockSectionsByTd[nTradingDay][nStockId].d_fa_yoyocf)
        return True


    def GetStockSectionValue(self, euSs, strStockWindCode, nTradingDay):
        if (isinstance(euSs, EU_StockSection) == False):
            return None
        nStockId = strStockWindCode
        if (isinstance(strStockWindCode, str) == True):
            nStockId = stockCn.StockWindCode2Int(strStockWindCode)
        if (nStockId == None):
            return None
        if (nTradingDay not in self.__dictStockSectionsByTd.keys()):
            return None
        if (nStockId not in self.__dictStockSectionsByTd[nTradingDay].keys()):
            return None

        dValue = None
        if (euSs == euSs_Pe):
            dValue = self.dPe
        elif (euSs == euSs_Pb):
            dValue = self.dPb
        elif (euSs == euSs_Pcf):
            dValue = self.dPcf
        elif (euSs == euSs_Ps):
            dValue = self.dPs
        elif (euSs == euSs_MarketValueTotal):
            dValue = self.d_val_mv
        elif (euSs == euSs_MarketValueFlowing):
            dValue = self.d_dq_mv
        elif (euSs == euSs_MarketValueFlowingFree):
            dValue = self.d_freefloat_mv
        elif (euSs == euSs_Qfa_yoynetprofit):
            dValue = self.d_qfa_yoynetprofit
        elif (euSs == euSs_Qfa_yoysales):
            dValue = self.d_qfa_yoysales
        elif (euSs == euSs_Fa_yoyroe):
            dValue = self.d_fa_yoyroe
        elif (euSs == euSs_Fa_yoyocf):
            dValue = self.d_fa_yoyocf
        elif (euSs == euSs_Fa_yoy_equity):
            dValue = self.d_fa_yoy_equity
        return dValue

    def GetStockSectionElem(self, euSs, nStockId, nTradingDay):
        dValue = self.GetStockSectionValue
        if (dValue == None):
            return None
        return CStockSectionElem(nStockId, nTradingDay, euSs, dValue)

    def Print(self):
        for nTd in self.__dictStockSectionsByTd.keys():
            for nStockId in self.__dictStockSectionsByTd[nTd].keys():
                print(nTd, nStockId \
                    , self.__dictStockSectionsByTd[nTd][nStockId].dPe \
                    , self.__dictStockSectionsByTd[nTd][nStockId].dPb \
                    , self.__dictStockSectionsByTd[nTd][nStockId].dPcf \
                    , self.__dictStockSectionsByTd[nTd][nStockId].dPs \
                    , self.__dictStockSectionsByTd[nTd][nStockId].d_val_mv \
                    , self.__dictStockSectionsByTd[nTd][nStockId].d_dq_mv \
                    , self.__dictStockSectionsByTd[nTd][nStockId].d_freefloat_mv \
                    , self.__dictStockSectionsByTd[nTd][nStockId].d_freeshared_today \
                    , self.__dictStockSectionsByTd[nTd][nStockId].d_qfa_yoynetprofit \
                    , self.__dictStockSectionsByTd[nTd][nStockId].d_qfa_yoysales \
                    , self.__dictStockSectionsByTd[nTd][nStockId].d_fa_yoy_equity \
                    , self.__dictStockSectionsByTd[nTd][nStockId].d_fa_yoyroe \
                    , self.__dictStockSectionsByTd[nTd][nStockId].d_fa_yoyocf)



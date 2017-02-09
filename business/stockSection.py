# -*- coding:utf-8 -*-
# Create On 20161222
# Auth: wang.yijian
# desc: 股票因子

import sys;sys.path.append("../")
from enum import Enum
import business.stockCn as stockCn
import utils.dateTime as dateTime

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


dictStr2Ss = { "pe":EU_StockSection.euSs_Pe, \
    "pb":EU_StockSection.euSs_Pb, \
    "pcf":EU_StockSection.euSs_Pcf, \
    "ps":EU_StockSection.euSs_Ps, \
    "mv":EU_StockSection.euSs_MarketValueTotal, \
    "dqmv":EU_StockSection.euSs_MarketValueFlowing, \
    "fdqmv":EU_StockSection.euSs_MarketValueFlowingFree, \
    "yoynetprofit":EU_StockSection.euSs_Qfa_yoynetprofit, \
    "yoysales":EU_StockSection.euSs_Qfa_yoysales, \
    "yoyequity":EU_StockSection.euSs_Fa_yoy_equity, \
    "yoyroe":EU_StockSection.euSs_Fa_yoyroe, \
    "yoyocf":EU_StockSection.euSs_Fa_yoyocf, \
    "roededucted":EU_StockSection.euSs_Qfa_roe_deducted }
    
def SsToString(euSs):
    for strSs in dictStr2Ss.keys():
        if dictStr2Ss[strSs] == euSs:
            return strSs
    return ""
    
def SsFromString(strSs):
    if strSs not in dictStr2Ss.keys():
        return EU_StockSection.euSs_None
    else:
        return dictStr2Ss[strSs]
    """
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
    """
# print(SsFromString('yoyocf').value)

def DfColFromEuSs(euSs):
    if (euSs == EU_StockSection.euSs_Pe):
        return "S_VAL_PE_TTM"
    elif (euSs == EU_StockSection.euSs_Pb):
        return "S_VAL_PB_NEW"
    elif (euSs == EU_StockSection.euSs_Pcf):
        return "S_VAL_PCF_OCFTTM"
    elif (euSs == EU_StockSection.euSs_Ps):
        return "S_VAL_PS_TTM"
    elif (euSs == EU_StockSection.euSs_MarketValueTotal):
        return "S_VAL_MV"
    elif (euSs == EU_StockSection.euSs_MarketValueFlowing):
        return "S_DQ_MV"
    elif (euSs == EU_StockSection.euSs_MarketValueFlowingFree):
        return "MVFlowingFree"
    elif (euSs == EU_StockSection.euSs_Qfa_yoynetprofit):
        return "S_QFA_YOYNETPROFIT"
    elif (euSs == EU_StockSection.euSs_Qfa_yoysales):
        return "S_QFA_YOYSALES"
    elif (euSs == EU_StockSection.euSs_Fa_yoy_equity):
        return "S_FA_YOY_EQUITY"
    elif (euSs == EU_StockSection.euSs_Fa_yoyroe):
        return "S_FA_YOYROE"
    elif (euSs == EU_StockSection.euSs_Fa_yoyocf):
        return "S_FA_YOYOCF"
    else:
        return ""


class CStockSectionElem(object):
    def __init__(self, nStockId, nTradingDay, euSs, dSectionValue):
        self.__nStockId = stockCn.StockWindCode2Int(nStockId)
        self.__nTradingDay = nTradingDay
        if (isinstance(nTradingDay, int) == False):
            strTradingDay = dateTime.ToIso(nTradingDay)
            if (strTradingDay == None):
                return None
            self.__nTradingDay = int(strTradingDay)
        self.__euSs = euSs
        self.__dValue = dSectionValue

    def __lt__(self, rhs):
        return self.__dValue < rhs.GetValue()
    def __eq__(self, rhs):
        return self.__dValue == rhs.GetValue() and self.__nStockId == rhs.GetStockId() and self.__nTradingDay == rhs.GetTradingDay() and self.__euSs == rhs.GetSectionId()
    def __hash__(self):
        return hash(str(self.__nStockId) + " " + str(self.__nTradingDay) + " " + str(self.__euSs.value) + " " + str(self.__dValue))

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

    def Clear(self):
        self.__dictStockSectionsByTd.clear()

    # 删除dtBefore 之前的记录
    def RemoveBefore(self, dtBefore):
        nBefore = dtBefore
        print(1)
        if (isinstance(dtBefore, int) == False):
            print(2)
            strBefore = dateTime.ToIso(dtBefore)
            if (strBefore == None):
                print(3, strBefore, dtBefore)
                return False
            print(4)
            nBefore = int(strBefore)

        for key in list(self.__dictStockSectionsByTd.keys()):
            if (key <= nBefore):
                del self.__dictStockSectionsByTd[key]
        print(5)
        # self.Print()

    def Remove(self, dtFrom, dtTo):
        nFrom = dtFrom
        if (isinstance(dtFrom, int) == False):
            strFrom = dateTime.ToIso(dtFrom)
            if (strFrom == None):
                return False
            nFrom = int(strFrom)
        nTo = dtTo
        if (isinstance(nTo, int) == False):
            strTo = dateTime.ToIso(nTo)
            if (strTo == None):
                return False
            nTo = int(strTo)
        for key in self.__dictStockSectionsByTd.keys():
            if (key >= nFrom and key <= nTo):
                del self.__dictStockSectionsByTd[key]
        pass

    def AddValue1(self, strStockWindCode, nTradingDay, dPe, dPb, dPcf, dPs, d_val_mv, d_dq_mv, d_freeshared_today):
        nStockId = stockCn.StockWindCode2Int(strStockWindCode)
        if (nStockId == None):
            return False
        nTradingDayFix = nTradingDay
        if (isinstance(nTradingDay, int) == False):
            strTradingDay = dateTime.ToIso(nTradingDay)
            if (strTradingDay == None):
                return False
            nTradingDayFix = int(strTradingDay)

        if (nTradingDayFix not in self.__dictStockSectionsByTd.keys()):
            self.__dictStockSectionsByTd[nTradingDayFix] = {}
        if (nStockId not in self.__dictStockSectionsByTd[nTradingDayFix].keys()):
            self.__dictStockSectionsByTd[nTradingDayFix][nStockId] = CStockSectionRecord()

        self.__dictStockSectionsByTd[nTradingDayFix][nStockId].dPe = dPe
        self.__dictStockSectionsByTd[nTradingDayFix][nStockId].dPb = dPb
        self.__dictStockSectionsByTd[nTradingDayFix][nStockId].dPcf = dPcf
        self.__dictStockSectionsByTd[nTradingDayFix][nStockId].dPs = dPs
        self.__dictStockSectionsByTd[nTradingDayFix][nStockId].d_val_mv = d_val_mv
        self.__dictStockSectionsByTd[nTradingDayFix][nStockId].d_dq_mv = d_dq_mv
        self.__dictStockSectionsByTd[nTradingDayFix][nStockId].d_freeshared_today = d_freeshared_today
        # print(strStockWindCode, nTradingDayFix, self.__dictStockSectionsByTd[nTradingDayFix][nStockId].dPe \
        #     , self.__dictStockSectionsByTd[nTradingDayFix][nStockId].dPb \
        #     , self.__dictStockSectionsByTd[nTradingDayFix][nStockId].dPcf \
        #     , self.__dictStockSectionsByTd[nTradingDayFix][nStockId].dPs \
        #     , self.__dictStockSectionsByTd[nTradingDayFix][nStockId].d_val_mv \
        #     , self.__dictStockSectionsByTd[nTradingDayFix][nStockId].d_dq_mv \
        #     , self.__dictStockSectionsByTd[nTradingDayFix][nStockId].d_freeshared_today)
        return True

    def AddValue2(self, strStockWindCode, nTradingDay, d_qfa_yoynetprofit, d_qfa_yoysales, d_fa_yoy_equity, d_fa_yoyroe, d_fa_yoyocf):
        nStockId = stockCn.StockWindCode2Int(strStockWindCode)
        if (nStockId == None):
            return False
        nTradingDayFix = nTradingDay
        if (isinstance(nTradingDay, int) == False):
            strTradingDay = dateTime.ToIso(nTradingDay)
            if (strTradingDay == None):
                return False
            nTradingDayFix = int(strTradingDay)

        if (nTradingDayFix not in self.__dictStockSectionsByTd.keys()):
            self.__dictStockSectionsByTd[nTradingDayFix] = {}
        if (nStockId not in self.__dictStockSectionsByTd[nTradingDayFix].keys()):
            self.__dictStockSectionsByTd[nTradingDayFix][nStockId] = CStockSectionRecord()

        self.__dictStockSectionsByTd[nTradingDayFix][nStockId].d_qfa_yoynetprofit = d_qfa_yoynetprofit
        self.__dictStockSectionsByTd[nTradingDayFix][nStockId].d_qfa_yoysales = d_qfa_yoysales
        self.__dictStockSectionsByTd[nTradingDayFix][nStockId].d_fa_yoy_equity = d_fa_yoy_equity
        self.__dictStockSectionsByTd[nTradingDayFix][nStockId].d_fa_yoyroe = d_fa_yoyroe
        self.__dictStockSectionsByTd[nTradingDayFix][nStockId].d_fa_yoyocf = d_fa_yoyocf
        # self.__dictStockSectionsByTd[nTradingDayFix][nStockId].d_qfa_roe_deducted = d_qfa_roe_deducted
        # print(strStockWindCode, nTradingDayFix, self.__dictStockSectionsByTd[nTradingDayFix][nStockId].d_qfa_yoynetprofit \
        #     , self.__dictStockSectionsByTd[nTradingDayFix][nStockId].d_qfa_yoysales \
        #     , self.__dictStockSectionsByTd[nTradingDayFix][nStockId].d_fa_yoy_equity \
        #     , self.__dictStockSectionsByTd[nTradingDayFix][nStockId].d_fa_yoyroe \
        #     , self.__dictStockSectionsByTd[nTradingDayFix][nStockId].d_fa_yoyocf)
        return True


    def GetStockSectionValue(self, euSs, strStockWindCode, dtTradingDay):
        if (isinstance(euSs, EU_StockSection) == False):
            print('GetStockSectionValue: euSs is not instance of EU_StockSection: ', euSs)
            return None
        nStockId = stockCn.StockWindCode2Int(strStockWindCode)
        if (nStockId == None):
            print('GetStockSectionValue: strStockWindCode Error: ', nStockId)
            return None
        nTradingDay = dtTradingDay
        if (isinstance(dtTradingDay, int) == False):
            strTradingDay = dateTime.ToIso(dtTradingDay)
            if (strTradingDay == None):
                return None
            nTradingDay = int(strTradingDay)
        if (nTradingDay == None):
            print('GetStockSectionValue: dtTradingDay Error: ', dtTradingDay)
        if (nTradingDay not in self.__dictStockSectionsByTd.keys()):
            print('GetStockSectionValue: nTradingDay is not in : ', nTradingDay)
            return None
        if (nStockId not in self.__dictStockSectionsByTd[nTradingDay].keys()):
            print('GetStockSectionValue: nStockId is not in : ', nStockId)
            return None

        dValue = None
        if (euSs == EU_StockSection.euSs_Pe):
            dValue = self.__dictStockSectionsByTd[nTradingDay][nStockId].dPe
        elif (euSs == EU_StockSection.euSs_Pb):
            dValue = self.__dictStockSectionsByTd[nTradingDay][nStockId].dPb
        elif (euSs == EU_StockSection.euSs_Pcf):
            dValue = self.__dictStockSectionsByTd[nTradingDay][nStockId].dPcf
        elif (euSs == EU_StockSection.euSs_Ps):
            dValue = self.__dictStockSectionsByTd[nTradingDay][nStockId].dPs
        elif (euSs == EU_StockSection.euSs_MarketValueTotal):
            dValue = self.__dictStockSectionsByTd[nTradingDay][nStockId].d_val_mv
        elif (euSs == EU_StockSection.euSs_MarketValueFlowing):
            dValue = self.__dictStockSectionsByTd[nTradingDay][nStockId].d_dq_mv
        elif (euSs == EU_StockSection.euSs_MarketValueFlowingFree):
            dValue = self.__dictStockSectionsByTd[nTradingDay][nStockId].d_freefloat_mv
        elif (euSs == EU_StockSection.euSs_Qfa_yoynetprofit):
            dValue = self.__dictStockSectionsByTd[nTradingDay][nStockId].d_qfa_yoynetprofit
        elif (euSs == EU_StockSection.euSs_Qfa_yoysales):
            dValue = self.__dictStockSectionsByTd[nTradingDay][nStockId].d_qfa_yoysales
        elif (euSs == EU_StockSection.euSs_Fa_yoyroe):
            dValue = self.__dictStockSectionsByTd[nTradingDay][nStockId].d_fa_yoyroe
        elif (euSs == EU_StockSection.euSs_Fa_yoyocf):
            dValue = self.__dictStockSectionsByTd[nTradingDay][nStockId].d_fa_yoyocf
        elif (euSs == EU_StockSection.euSs_Fa_yoy_equity):
            dValue = self.__dictStockSectionsByTd[nTradingDay][nStockId].d_fa_yoy_equity
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


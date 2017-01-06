# -*- coding:utf-8 -*-
# Create On 20170103
# Auth: wang.yijian
# desc: 指数成分

import sys;sys.path.append("../")
import business.mdBar as mdBar

class CPosition_Index(object):
    def __init__(self):
        self.dtTradingDay = ''      # TradingDay
        self.nStockId = None
        self.nSsId = 0
        self.dPosition = 0.0        # 总持仓数量
        self.dWeight = 0.0          # 比重
        self.dMarketValue = 0.0     # 总市值
        self.dLastPrice = 0.0       # 最新价
        self.timeLastPrice = 0.0    # 最新价时间

        self.dGrade1 = 0.0
        self.dGrade2 = 0.0
        self.dGrade3 = 0.0
        self.dGrade4 = 0.0

    def Print(self):
        print(self.dtTradingDay, self.nStockId, self.nSsId, self.dPosition, self.dWeight, self.dMarketValue, self.dLastPrice, self.timeLastPrice  , self.dGrade1, self.dGrade2, self.dGrade3, self.dGrade4)

    def CalcPosition(self):
        if (self.dLastPrice == 0.0 or self.dMarketValue == 0.0):
            return 0.0
        self.dPosition = self.dMarketValue / self.dLastPrice
        return self.dPosition

    def CalcPosWeight(self, dTotalMv):
        self.dWeight = self.dMarketValue / dTotalMv
        return self.dWeight

    def CalcMarketValue(self):
        if (self.dLastPrice == 0.0 or self.dPosition == 0.0):
            return 0.0
        self.dMarketValue = self.dLastPrice * self.dPosition
        return self.dMarketValue

    def FlushMd(self):
        mdBarMgr = mdBar.CMdBarDataManager()
        listPrice = mdBarMgr.GetPrice(mdBar.EU_MdBarInterval.mdbi_1d, self.nStockId, self.dtTradingDay)
        if (listPrice == None or len(listPrice) == 0):
            return False
        self.dLastPrice = listPrice[3]


class CPositionSet_Index(object):
    def __init__(self):
        self.dictPositions = {}         # instrumentId -> CPosition_Index
        self.dTotalMarketValue = 0.0
        pass

    def Add(self, pos):
        if (isinstance(pos, CPosition_Index) == False):
            return None
        nInstId = stockCn.StockWindCode2Int(pos.nStockId)
        pos.nStockId = nInstId
        self.dictPositions[nInstId] = pos

    def SetPosTradingDay(self, dtTradingDay):
        for key in self.dictPositions.keys():
            self.dictPositions[key].dtTradingDay = dtTradingDay

    def CalcTotalMarketValue(self):
        dTotalMarketValue = 0.0
        for key in self.dictPositions.keys():
            dMarketValue = self.dictPositions[key].CalcMarketValue()
            if (dMarketValue != 0.0):
                dTotalMarketValue += dMarketValue
        self.dTotalMarketValue = dTotalMarketValue
        return dTotalMarketValue

    def CalcPosPosition(self):
        for key in self.dictPositions.keys():
            self.dictPositions[key].CalcPosition()

    def CalcPosWeight(self):
        for key in self.dictPositions.keys():
            self.dictPositions[key].CalcPosWeight(self.dTotalMarketValue)

    def FlushMd(self):
        for key in self.dictPositions.keys():
            self.dictPositions[key].FlushMd()

    def Print(self):
        print(len(self.dictPositions), self.dTotalMarketValue)
        for key in self.dictPositions.keys():
            self.dictPositions[key].Print()

# pos1 = CPosition_Index()
# pos1.dMarketValue = 1000.0
# pos1.nStockId = 'aaaaaa'
# pos1.dLastPrice = 13.2
#
# pos2 = CPosition_Index()
# pos2.dMarketValue = 1003.0
# pos2.nStockId = 'bbbbbb'
# pos2.dLastPrice = 24.4
#
# posset = CPositionSet_Index()
# posset.dictPositions[pos1.nStockId] = pos1
# posset.dictPositions[pos2.nStockId] = pos2
#
# posset.CalcPosPosition()
# posset.SetPosTradingDay('20120101')
# posset.CalcTotalMarketValue()
# posset.CalcPosWeight()
# posset.Print()#

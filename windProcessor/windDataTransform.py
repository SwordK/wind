# -*- coding:utf-8 -*-
# Create On 20161221
# Auth: wang.yijian
# desc: wind 量化接口 数据处理

import time
# return: list
# list[0]: fields
# list[1]: datas

# wsetResult {
def wsetResult(wsetdata):
    if (wsetdata.ErrorCode != 0):
        return None
    codesLen = len(wsetdata.Codes)
    fieldsLen = len(wsetdata.Fields)
    timesLen = len(wsetdata.Times)
    dataLen = len(wsetdata.Data)

    if (codesLen <= 0):
        print('wsetResult: codesLen[' + str(codesLen) + '] <= 0')
        return None
    if (fieldsLen <= 0):
        print('wsetResult: fields[' + str(fieldsLen) + '] <= 0')
        return None
    if (timesLen <= 0):
        print('wsetResult: timesLen[' + str(timesLen) + '] <= 0')
        return None
    if (dataLen <= 0):
        print('wsetResult: dataLen[' + str(dataLen) + '] <= 0')
        return None
    if (fieldsLen != dataLen):
        print('wsetResult: fieldsLen[' + str(fieldsLen) + '] != dataLen[' + str(dataLen) + ']')
        return None

    dataCount = len(wsetdata.Data[0])
    strDateTime = wsetdata.Times[0].strftime('%Y-%m-%d %H:%M:%S.%f')
    listFields = ['STime']
    listFields += wsetdata.Fields
    listResult = []
    for dataIndex in range(0, dataCount):
        listRow = []

        listRow.append(strDateTime)
        for fieldIndex in range(0, fieldsLen):
            strTemp = str(wsetdata.Data[fieldIndex][dataIndex])
            listRow.append(strTemp)

        listResult.append(listRow)
    return listFields, listResult
# } end of wsetResult

# wsdResult {
def wsdResult(wsddata):
    if (wsddata.ErrorCode != 0):
        print('wsddata.ErrorCode:' + str(wsddata.ErrorCode))
        return None
    codesLen = len(wsddata.Codes)
    fieldsLen = len(wsddata.Fields)
    timesLen = len(wsddata.Times)
    dataLen = len(wsddata.Data)

    if (codesLen != 1):
        print('wsdResult: codesLen[' + str(codesLen) + '] != 1')
        return None
    if (fieldsLen <= 0):
        print('wsdResult: fieldsLen[' + str(fieldsLen) + '] <= 0')
        return None
    if (timesLen <= 0):
        print('wsdResult: timesLen[' + str(timesLen) + '] <= 0')
        return None
    if (dataLen <= 0):
        print('wsdResult: dataLen[' + str(dataLen) + '] <= 0')
        return None
    if (fieldsLen != dataLen):
        print('wsdResult: fieldsLen[' + str(fieldsLen) + '] != dataLen[' + str(dataLen) + ']')
        return None

    dataCount = len(wsddata.Data[0])
    if (timesLen != dataCount):
        print('wsdResult: timesLen[' + str(timesLen) + '] != dataCount[' + str(dataCount) + ']')
        return None

    listFields = []
    listFields.append('SInstrument')
    listFields.append('STime')
    listFields += wsddata.Fields
    listResult = []

    for dataIndex in range(0, dataCount):
        strDateTime = wsddata.Times[dataIndex].strftime('%Y-%m-%d %H:%M:%S.%f')
        listRow = []
        listRow.append(wsddata.Codes[0])
        listRow.append(strDateTime)

        for fieldIndex in range(0, fieldsLen):
            strTemp = str(wsddata.Data[fieldIndex][dataIndex])
            listRow.append(strTemp)

        listResult.append(listRow)
    return listFields, listResult
    pass
# } end of wsdResult

# wsiResult {
def wsiResult(wsidata):
    if (wsidata.ErrorCode != 0):
        return None
    codesLen = len(wsidata.Codes)
    fieldsLen = len(wsidata.Fields)
    timesLen = len(wsidata.Times)
    dataLen = len(wsidata.Data)

    if (codesLen != 1):
        print('wsiResult: codesLen[' + str(codesLen) + '] != 1')
        return None
    if (fieldsLen <= 0):
        print('wsiResult: fieldsLen[' + str(fieldsLen) + '] <= 0')
        return None
    if (timesLen <= 0):
        print('wsiResult: timesLen[' + str(timesLen) + '] <= 0')
        return None
    if (dataLen <= 0):
        print('wsiResult: dataLen[' + str(dataLen) + '] <= 0')
        return None

    listFields = []
    listResult = []
    if (wsidata.Codes[0] != 'MultiCodes'):
        # print('wsidata.Codes[0] != MultiCodes', wsidata.Codes[0])
        listFields.append('STime')
        listFields.append('SInstrument')
    else:
        pass

    listFields += wsidata.Fields

    dataCount = len(wsidata.Data[0])
    for dataIndex in range(0, dataCount):
        listRow = []
        if (wsidata.Codes[0] != 'MultiCodes'):
            strDateTime = wsidata.Times[dataIndex].strftime('%Y-%m-%d %H:%M:%S.%f')
            listRow.append(strDateTime)
            listRow.append(wsidata.Codes[0])

        for fieldIndex in range(0, fieldsLen):
            strTemp = str(wsidata.Data[fieldIndex][dataIndex])
            listRow.append(strTemp)

        listResult.append(listRow)
    return listFields, listResult
# } end of wsiResult

# wssResult {
def wssResult(wssdata):
    if (wssdata.ErrorCode != 0):
        return None
    codesLen = len(wssdata.Codes)
    fieldsLen = len(wssdata.Fields)
    timesLen = len(wssdata.Times)
    dataLen = len(wssdata.Data)

    if (codesLen <= 0):
        print('wssResult: codesLen[' + str(codesLen) + '] <= 0')
        return None
    if (fieldsLen <= 0):
        print('wssResult: fieldsLen[' + str(fieldsLen) + '] <= 0')
        return None
    if (timesLen <= 0):
        print('wssResult: timesLen[' + str(timesLen) + '] <= 0')
        return None
    if (dataLen <= 0):
        print('wssResult: dataLen[' + str(dataLen) + '] <= 0')
        return None

    dataCount = len(wssdata.Data[0])
    if (codesLen != dataCount):
        print('wssResult: codesLen[' + str(codesLen) + '] != dataCount[' + str(dataCount) + ']')
        return None

    strDateTime = wssdata.Times[0].strftime('%Y-%m-%d %H:%M:%S.%f')
    listFields = []
    listFields.append('SInstrument')
    listFields.append('STime')
    listFields += wssdata.Fields
    listResult = []
    for dataIndex in range(0, dataCount):
        listRow = []
        listRow.append(strDateTime)
        listRow.append(wssdata.Codes[dataIndex])

        for fieldIndex in range(0, fieldsLen):
            strTemp = str(wssdata.Data[fieldIndex][dataIndex])
            listRow.append(strTemp)

        listResult.append(listRow)
    return listFields, listResult
# } end of wssResult

"""
# main {
if __name__ == '__main__':
    w.start()

    print('1. *******************************************************')
    strReportName = "sectorconstituent"
    strInputParam = 'date=2016-12-21;sectorid=a599010102000000'
    windData = w.wset(strReportName, strInputParam)
    listR = wsetResult(windData)
    if (listR == None):
        exit(-1)
    listFields = listR[0]
    listResult = listR[1]
    print(listFields)
    for row in listResult:
        print(row)

    print('2. *******************************************************')
    strReportName = 'optionchain'
    strInputParam = 'date=2016-12-21;us_code=510050.SH;option_var=全部;month=全部;call_put=全部'
    windData = w.wset(strReportName, strInputParam)
    listR = wsetResult(windData)
    if (listR == None):
        print('2')
        exit(-1)
    listFields = listR[0]
    listResult = listR[1]
    print(listFields)
    for row in listResult:
        print(row)

    print('3. *******************************************************')
    windData = w.wsd("000010.SZ", "open,low,high,close,volume,amt", "2016-11-21", "2016-12-20", "")
    listR = wsdResult(windData)
    if (listR == None):
        print('3')
        exit(-1)
    listFields = listR[0]
    listResult = listR[1]
    print(listFields)
    for row in listResult:
        print(row)

    print('4. *******************************************************')
    windData = w.wsi("000010.SZ", "open,high,low,close,volume,amt", "2016-12-19 09:00:00", "2016-12-21 15:50:16", "BarSize=60")
    listR = wsiResult(windData)
    if (listR == None):
        exit(-1)
    listFields = listR[0]
    listResult = listR[1]
    print(listFields)
    for row in listResult:
        print(row)

    print('5. *******************************************************')
    windData = w.wsi("600000.SH,000010.SZ", "open,high,low,close,volume,amt", "2016-12-19 09:00:00", "2016-12-21 15:50:16", "BarSize=60")
    listR = wsiResult(windData)
    if (listR == None):
        exit(-1)
    listFields = listR[0]
    listResult = listR[1]
    print(listFields)
    for row in listResult:
        print(row)

    print('6. *******************************************************')
    windData = w.wss("600008.SH,600017.SH", "open,low,high,close,volume,amt","tradeDate=20161219;priceAdj=U;cycle=D")
    print(windData)
    print('')
    listR = wssResult(windData)
    if (listR == None):
        exit(-1)
    listFields = listR[0]
    listResult = listR[1]
    print(listFields)
    for row in listResult:
        print(row)
# } end of main
"""

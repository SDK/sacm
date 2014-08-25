# -*- coding: utf-8 -*-
__author__ = 'sdk'
from sacm import *
from xml.dom import minidom
import pandas as pd

asdmUID = ''

def getASDM(uid=None):
    asdmXML = GetXML(uid,'ASDM')
    asdm = minidom.parseString(asdmXML)
    rows = asdm.getElementsByTagName('Table')
    asdmList = list()
    for i in rows:
        if int(i.getElementsByTagName('NumberRows')[0].firstChild.data) != 0:
            #print i.getElementsByTagName('Name')[0].firstChild.data,i.getElementsByTagName('NumberRows')[0].firstChild.data
            asdmList.append((i.getElementsByTagName('Name')[0].firstChild.data,
                             i.getElementsByTagName('NumberRows')[0].firstChild.data,
                             str(i.getElementsByTagName('Entity')[0].getAttribute('entityTypeName')),
                             str(i.getElementsByTagName('Entity')[0].getAttribute('entityId'))))
    return asdmList, pd.DataFrame(asdmList, columns=['table', 'numrows', 'typename', 'uid'])

def getMain(uid=None):
    mainXML = GetXML(uid,'Main')
    main = minidom.parseString(mainXML)
    mainList = list()
    rows = main.getElementsByTagName('row')
    for i in rows:
        #print i.getElementsByTagName('time')[0].firstChild.data, i.getElementsByTagName('stateId')[0].firstChild.data
        mainList.append((sdmTimeString(int(i.getElementsByTagName('time')[0].firstChild.data)),
                         #i.getElementsByTagName('numAntenna')[0].firstChild.data,
                         i.getElementsByTagName('timeSampling')[0].firstChild.data,
                         int(i.getElementsByTagName('interval')[0].firstChild.data),
                         #i.getElementsByTagName('numIntegration')[0].firstChild.data,
                         int(i.getElementsByTagName('scanNumber')[0].firstChild.data),
                         int(i.getElementsByTagName('subscanNumber')[0].firstChild.data),
                         int(i.getElementsByTagName('dataSize')[0].firstChild.data),
                         i.getElementsByTagName('dataUID')[0].getElementsByTagName('EntityRef')[0].getAttribute('entityId'),
                         i.getElementsByTagName('fieldId')[0].firstChild.data,
                         i.getElementsByTagName('stateId')[0].firstChild.data))
    return pd.DataFrame(mainList, columns=['time', 'timeSampling', 'interval', 'scanNumber',
                                         'subscanNumber', 'dataSize', 'dataUID', 'fieldId', 'stateId'])

def getScan(uid=None):
    scanXML = GetXML(uid,'Scan')
    scan = minidom.parseString(scanXML)
    scanList = list()
    rows = scan.getElementsByTagName('row')
    for i in rows:
        scanList.append((int(i.getElementsByTagName('scanNumber')[0].firstChild.data),
                         int(i.getElementsByTagName('startTime')[0].firstChild.data),
                         int(i.getElementsByTagName('endTime')[0].firstChild.data),
                         #i.getElementsByTagName('numIntent')[0].firstChild.data,
                         int(i.getElementsByTagName('numSubscan')[0].firstChild.data),
                         arrayParser(i.getElementsByTagName('scanIntent')[0].firstChild.data, 1),
                         arrayParser(i.getElementsByTagName('calDataType')[0].firstChild.data, 1),
                         int(i.getElementsByTagName('numField')[0].firstChild.data),
                         i.getElementsByTagName('fieldName')[0].firstChild.data,
                         i.getElementsByTagName('sourceName')[0].firstChild.data))

    return pd.DataFrame(scanList, columns=['scanNumber', 'startTime', 'endTime', 'numSubscan',
                                         'scanIntent', 'calDataType', 'numField', 'fieldName', 'sourceName'])

def getSubScan(uid=None):
    subscanXML = GetXML(uid,'Subscan')
    subscan = minidom.parseString(subscanXML)
    subscanList = list()
    rows = subscan.getElementsByTagName('row')
    for i in rows:
        subscanList.append((int(i.getElementsByTagName('scanNumber')[0].firstChild.data),
                            int(i.getElementsByTagName('subscanNumber')[0].firstChild.data),
                            int(i.getElementsByTagName('startTime')[0].firstChild.data),
                            int(i.getElementsByTagName('endTime')[0].firstChild.data),
                            i.getElementsByTagName('fieldName')[0].firstChild.data,
                            i.getElementsByTagName('subscanIntent')[0].firstChild.data,
                            i.getElementsByTagName('subscanMode')[0].firstChild.data,
                            #i.getElementsByTagName('numIntegration')[0].firstChild.data,
                            #i.getElementsByTagName('numSubintegration')[0].firstChild.data,
                            #i.getElementsByTagName('correlatorCalibration')[0].firstChild.data
                            ))
    return pd.DataFrame(subscanList, columns=['scanNumber','subscanNumber','startTime','endTime','fieldName',
                                              'subscanIntent','subscanMode'])

def getSource(uid=None):
    sourceXML = GetXML(uid,'Source')
    source = minidom.parseString(sourceXML)
    sourceList = list()
    rows = source.getElementsByTagName('row')
    #there are missing fields in some rows for the Source table.
    for i in rows:
        try:
            sourceList.append((int(i.getElementsByTagName('sourceId')[0].firstChild.data),
                               i.getElementsByTagName('timeInterval')[0].firstChild.data,
                               i.getElementsByTagName('direction')[0].firstChild.data,
                               i.getElementsByTagName('directionCode')[0].firstChild.data,
                               i.getElementsByTagName('sourceName')[0].firstChild.data,
                               i.getElementsByTagName('spectralWindowId')[0].firstChild.data,
                               i.getElementsByTagName('frequency')[0].firstChild.data,
                               arrayParser(i.getElementsByTagName('flux')[0].firstChild.data,2),
                               int(i.getElementsByTagName('numStokes')[0].firstChild.data)))
        except IndexError as e:
            sourceList.append((int(i.getElementsByTagName('sourceId')[0].firstChild.data),
                               i.getElementsByTagName('timeInterval')[0].firstChild.data,
                               i.getElementsByTagName('direction')[0].firstChild.data,
                               i.getElementsByTagName('directionCode')[0].firstChild.data,
                               i.getElementsByTagName('sourceName')[0].firstChild.data,
                               i.getElementsByTagName('spectralWindowId')[0].firstChild.data))
    return pd.DataFrame(sourceList)

def getSpectralWindow(uid=None):
    spwXML = GetXML(uid,'SpectralWindow')
    spw = minidom.parseString(spwXML)
    spwList = list()
    rows = spw.getElementsByTagName('row')
    for i in rows:
        spwList.append((i.getElementsByTagName('spectralWindowId')[0].firstChild.data,
                        i.getElementsByTagName('basebandName')[0].firstChild.data,
                        i.getElementsByTagName('netSideband')[0].firstChild.data,
                        int(i.getElementsByTagName('numChan')[0].firstChild.data),
                        float(i.getElementsByTagName('refFreq')[0].firstChild.data),
                        i.getElementsByTagName('sidebandProcessingMode')[0].firstChild.data,
                        float(i.getElementsByTagName('totBandwidth')[0].firstChild.data),
                        #i.getElementsByTagName('chanFreqArray')[0].firstChild.data,
                        #i.getElementsByTagName('chanWidthArray')[0].firstChild.data,
                        #i.getElementsByTagName('effectiveBwArray')[0].firstChild.data,
                        i.getElementsByTagName('name')[0].firstChild.data,
                        #i.getElementsByTagName('resolutionArray')[0].firstChild.data,
                        i.getElementsByTagName('assocNature')[0].firstChild.data,
                        i.getElementsByTagName('assocSpectralWindowId')[0].firstChild.data))
    return pd.DataFrame(spwList, columns=['spectralWindowId', 'basebandName', 'netSideband', 'numChan',
                                         'refFreq', 'sidebandProcessingMode', 'totBandwidth', 'name',
                                         'assocNature', 'assocSpectralWindowId'])

def getField(uid=None):
    fieldXML = GetXML(uid,'Field')
    field = minidom.parseString(fieldXML)
    fieldList = list()
    rows = field.getElementsByTagName('row')
    for i in rows:
        fieldList.append((i.getElementsByTagName('fieldId')[0].firstChild.data,
                          i.getElementsByTagName('fieldName')[0].firstChild.data,
                          i.getElementsByTagName('numPoly')[0].firstChild.data,
                          #i.getElementsByTagName('delayDir')[0].firstChild.data,
                          #i.getElementsByTagName('phaseDir')[0].firstChild.data,
                          #i.getElementsByTagName('referenceDir')[0].firstChild.data,
                          int(i.getElementsByTagName('time')[0].firstChild.data),
                          i.getElementsByTagName('code')[0].firstChild.data,
                          i.getElementsByTagName('directionCode')[0].firstChild.data,
                          int(i.getElementsByTagName('sourceId')[0].firstChild.data)))
    return pd.DataFrame(fieldList, columns=['fieldId', 'fieldName', 'numPoly', 'time', 'code', 'directionCode', 'sourceId'])


def getSysCal(uid=None):
    syscalXML = GetXML(uid,'SysCal')
    syscal = minidom.parseString(syscalXML)
    syscalList = list()
    rows = syscal.getElementsByTagName('row')
    for i in rows:
        syscalList.append((
            i.getElementsByTagName('timeInterval')[0].firstChild.data,
            i.getElementsByTagName('numReceptor')[0].firstChild.data,
            i.getElementsByTagName('numChan')[0].firstChild.data,
            i.getElementsByTagName('tcalFlag')[0].firstChild.data,
            i.getElementsByTagName('tcalSpectrum')[0].firstChild.data,
            i.getElementsByTagName('trxFlag')[0].firstChild.data,
            i.getElementsByTagName('trxSpectrum')[0].firstChild.data,
            i.getElementsByTagName('tskyFlag')[0].firstChild.data,
            i.getElementsByTagName('tskySpectrum')[0].firstChild.data,
            i.getElementsByTagName('tsysFlag')[0].firstChild.data,
            i.getElementsByTagName('tsysSpectrum')[0].firstChild.data,
            i.getElementsByTagName('antennaId')[0].firstChild.data,
            i.getElementsByTagName('feedId')[0].firstChild.data,
            i.getElementsByTagName('spectralWindowId')[0].firstChild.data ))
    return pd.DataFrame(syscalList, columns=['timeInterval','numReceptor','numChan','tcalFlag','tcalSpectrum','trxFlag',
                                             'trxSpectrum','tskyFlag','tskySpectrum','tsysFlag','tsysSpectrum','antennaId',
                                             'feedId','spectralWindowId'])


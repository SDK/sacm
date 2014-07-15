# -*- coding: utf-8 -*-
__author__ = 'sdk'
from sacm import *
from xml.dom import minidom
import pandas as pd

asdmXML = open('uid___A002_X837c61_Xffd/ASDM.xml', 'r')

asdm = minidom.parse(asdmXML)
rows = asdm.getElementsByTagName('Table')
asdmList = list()
for i in rows:
    if int(i.getElementsByTagName('NumberRows')[0].firstChild.data) != 0:
        #print i.getElementsByTagName('Name')[0].firstChild.data,i.getElementsByTagName('NumberRows')[0].firstChild.data
        #print str(i.getElementsByTagName('Entity')[0].getAttribute('entityTypeName')),str(i.getElementsByTagName('Entity')[0].getAttribute('entityId'))
        asdmList.append((i.getElementsByTagName('Name')[0].firstChild.data,
                         i.getElementsByTagName('NumberRows')[0].firstChild.data,
                         str(i.getElementsByTagName('Entity')[0].getAttribute('entityTypeName')),
                         str(i.getElementsByTagName('Entity')[0].getAttribute('entityId'))))

for i in asdmList:
    if '/X0/X0/' in i[3]:
        FlagError['EmptyUID'] = True

mainXML = open('uid___A002_X837c61_Xffd/Main.xml', 'r')
main = minidom.parse(mainXML)
mainList = list()

rows = main.getElementsByTagName('row')
for i in rows:
    #print i.getElementsByTagName('time')[0].firstChild.data, i.getElementsByTagName('stateId')[0].firstChild.data
    mainList.append((sdmTimeString(int(i.getElementsByTagName('time')[0].firstChild.data)),
                     i.getElementsByTagName('numAntenna')[0].firstChild.data,
                     i.getElementsByTagName('timeSampling')[0].firstChild.data,
                     i.getElementsByTagName('interval')[0].firstChild.data,
                     i.getElementsByTagName('numIntegration')[0].firstChild.data,
                     i.getElementsByTagName('scanNumber')[0].firstChild.data,
                     i.getElementsByTagName('subscanNumber')[0].firstChild.data,
                     i.getElementsByTagName('dataSize')[0].firstChild.data,
                     i.getElementsByTagName('dataUID')[0].getElementsByTagName('EntityRef')[0].getAttribute('entityId'),
                     i.getElementsByTagName('fieldId')[0].firstChild.data,
                     (i.getElementsByTagName('stateId')[0].firstChild.data).split(' ')[2]))

for i in mainList:
    if 'null' in i[10]:
        FlagError['NullStateID'] = True


scanXML = open('uid___A002_X837c61_Xffd/Scan.xml', 'r')
scan = minidom.parse(scanXML)
scanList = list()
rows = scan.getElementsByTagName('row')

for i in rows:
    scanList.append((i.getElementsByTagName('scanNumber')[0].firstChild.data,
                     i.getElementsByTagName('startTime')[0].firstChild.data,
                     i.getElementsByTagName('endTime')[0].firstChild.data,
                     i.getElementsByTagName('numIntent')[0].firstChild.data,
                     i.getElementsByTagName('numSubscan')[0].firstChild.data,
                     arrayParser(i.getElementsByTagName('scanIntent')[0].firstChild.data, 1),
                     arrayParser(i.getElementsByTagName('calDataType')[0].firstChild.data, 1),
                     i.getElementsByTagName('numField')[0].firstChild.data,
                     i.getElementsByTagName('fieldName')[0].firstChild.data,
                     i.getElementsByTagName('sourceName')[0].firstChild.data))

subscanXML = open('uid___A002_X837c61_Xffd/Subscan.xml', 'r')
subscan = minidom.parse(subscanXML)
subscanList = list()
rows = subscan.getElementsByTagName('row')
for i in rows:
    subscanList.append((i.getElementsByTagName('scanNumber')[0].firstChild.data,
                        i.getElementsByTagName('subscanNumber')[0].firstChild.data,
                        i.getElementsByTagName('startTime')[0].firstChild.data,
                        i.getElementsByTagName('endTime')[0].firstChild.data,
                        i.getElementsByTagName('fieldName')[0].firstChild.data,
                        i.getElementsByTagName('subscanIntent')[0].firstChild.data,
                        i.getElementsByTagName('subscanMode')[0].firstChild.data,
                        i.getElementsByTagName('numIntegration')[0].firstChild.data,
                        i.getElementsByTagName('numSubintegration')[0].firstChild.data,
                        i.getElementsByTagName('correlatorCalibration')[0].firstChild.data))

sourceXML = open('uid___A002_X837c61_Xffd/Source.xml', 'r')
source = minidom.parse(sourceXML)
sourceList = list()
rows = source.getElementsByTagName('row')

#there are missing fields in some rows for the Source table.
for i in rows:
    sourceList.append((i.getElementsByTagName('sourceId')[0].firstChild.data,
                       i.getElementsByTagName('timeInterval')[0].firstChild.data,
                       i.getElementsByTagName('sourceName')[0].firstChild.data,
                       i.getElementsByTagName('spectralWindowId')[0].firstChild.data))

spwXML = open('uid___A002_X837c61_Xffd/SpectralWindow.xml', 'r')
spw = minidom.parse(spwXML)
spwList = list()
rows = spw.getElementsByTagName('row')

for i in rows:
    spwList.append((i.getElementsByTagName('spectralWindowId')[0].firstChild.data,
                    i.getElementsByTagName('basebandName')[0].firstChild.data,
                    i.getElementsByTagName('netSideband')[0].firstChild.data,
                    i.getElementsByTagName('numChan')[0].firstChild.data,
                    i.getElementsByTagName('refFreq')[0].firstChild.data,
                    i.getElementsByTagName('sidebandProcessingMode')[0].firstChild.data,
                    i.getElementsByTagName('totBandwidth')[0].firstChild.data,
                    #i.getElementsByTagName('chanFreqArray')[0].firstChild.data,
                    #i.getElementsByTagName('chanWidthArray')[0].firstChild.data,
                    #i.getElementsByTagName('effectiveBwArray')[0].firstChild.data,
                    i.getElementsByTagName('name')[0].firstChild.data,
                    #i.getElementsByTagName('resolutionArray')[0].firstChild.data,
                    i.getElementsByTagName('assocNature')[0].firstChild.data,
                    i.getElementsByTagName('assocSpectralWindowId')[0].firstChild.data))

fieldXML = open('uid___A002_X837c61_Xffd/Field.xml', 'r')
field = minidom.parse(fieldXML)
fieldList = list()
rows = field.getElementsByTagName('row')

for i in rows:
    fieldList.append((i.getElementsByTagName('fieldId')[0].firstChild.data,
                      i.getElementsByTagName('fieldName')[0].firstChild.data,
                      i.getElementsByTagName('numPoly')[0].firstChild.data,
                      i.getElementsByTagName('delayDir')[0].firstChild.data,
                      i.getElementsByTagName('phaseDir')[0].firstChild.data,
                      i.getElementsByTagName('referenceDir')[0].firstChild.data,
                      i.getElementsByTagName('time')[0].firstChild.data,
                      i.getElementsByTagName('code')[0].firstChild.data,
                      i.getElementsByTagName('directionCode')[0].firstChild.data,
                      i.getElementsByTagName('sourceId')[0].firstChild.data))


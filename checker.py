# -*- coding: utf-8 -*-
__author__ = 'sdk'
from sacm import *
from xml.dom import minidom

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
                     i.getElementsByTagName('scanIntent')[0].firstChild.data,
                     i.getElementsByTagName('calDataType')[0].firstChild.data,
                     i.getElementsByTagName('numField')[0].firstChild.data,
                     i.getElementsByTagName('fieldName')[0].firstChild.data,
                     i.getElementsByTagName('sourceName')[0].firstChild.data ))











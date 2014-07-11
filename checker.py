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


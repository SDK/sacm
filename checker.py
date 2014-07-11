__author__ = 'sdk'
from sacm import *
from xml.dom import minidom

asdmXML = open('uid___A002_X837c61_Xffd/ASDM.xml', 'r')

asdm = minidom.parse(asdmXML)
rows = asdm.getElementsByTagName('Table')
for i in rows:
    print i



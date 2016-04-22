#!/bin/env python
from MetaData import *
import pandas as pd
import cx_Oracle
import sys

try:
    orcl = cx_Oracle.connect(databaseSCO)
    cursor = orcl.cursor()
except Exception as e:
    sys.exit(1)

sql = """select SE_PROJECT_CODE,SE_EXECUTIVE,SE_SB_ID, SE_EB_UID from ALMA.SHIFTLOG_ENTRIES where se_sb_id in ('uid://A002/Xad2d3f/X3 ',
'uid://A001/X2fe/X267',
'uid://A001/X2fe/X268',
'uid://A001/X2fe/X26a',
'uid://A001/X2fe/X26b',
'uid://A001/X2fe/X26c',
'uid://A001/X2fe/X26e',
'uid://A001/X2fb/X638',
'uid://A001/X2d1/X25',
'uid://A002/Xaa5ac1/X36',
'uid://A002/Xb0eb5c/X6b',
'uid://A002/Xb0eb5c/X6d',
'uid://A002/Xb0eb5c/X6f',
'uid://A002/Xb0eb5c/X70',
'uid://A002/Xb0eb5c/X71',
'uid://A001/X2f6/X481',
'uid://A001/X2f6/X482',
'uid://A001/X2f6/X484',
'uid://A001/X2fb/X10e',
'uid://A001/X2de/Xa3',
'uid://A001/X2fb/X614',
'uid://A001/X2fb/X187',
'uid://A001/X2f6/Xf8',
'uid://A001/X2f6/Xf9',
'uid://A001/X2d8/X46') and SE_QA0FLAG = 'Pass' order by 2,1,3"""

cursor.execute(sql)
rows = cursor.fetchall()
text = '<html><head></head><body>'
a = AsdmCheck()
for i in rows:
    a.setUID(i[3])
    text += '<h3>'+i[0]+' ARC: '+str(i[1])+' SB: '+i[2]+' EB: '+i[3]+'</h3>'
    spw = getSpectralWindow(a.asdmDict['SpectralWindow'])
    scan = getScan(a.asdmDict['Scan'])
    source = getSource(a.asdmDict['Source'])
    scan['target'] = scan.apply(lambda x: True if str(x['scanIntent']).find('OBSERVE_TARGET') > 0 else False ,axis = 1)
    targets = map(unicode.strip,list(scan[scan['target'] == True].sourceName.values))
    source['target'] = source.apply(lambda x: True if str(x['sourceName']).strip() in targets else False, axis = 1)
    df = source[['spectralWindowId','target']].query('target == True')
    df1 = pd.merge(spw,df,left_on='spectralWindowId', right_on='spectralWindowId', how = 'inner')
    df1['freqStart'] = df1.apply(lambda x: float(x['chanFreqStart'])/1e9, axis = 1 )
    df1['freqEnd'] = df1.apply(lambda x: (float(x['chanFreqStart']) + float(x['totBandwidth']))/1e9 , axis = 1 )
    df1['centerFreq'] = df1.apply(lambda x: (x['freqStart'] + x['freqEnd'] )/2. , axis = 1 )
    df1['referenceFreq'] = df1.apply(lambda x: float(x['refFreq'])/1e9 , axis = 1 )
    text += df1[['spectralWindowId','basebandName','netSideband','numChan','referenceFreq','freqStart','freqEnd','centerFreq']].drop_duplicates().to_html()

text +='</body></html>'

html = open('sacm450.html','w')
html.write(text)
html.close()
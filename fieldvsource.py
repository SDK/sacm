__author__ = 'sagonzal'
from MetaData import *
import sys
import pandas as pd
import cx_Oracle
import pylab as pl

sql= """select SE_EB_UID, SE_SB_ID, SE_PROJECT_CODE from ALMA.SHIFTLOG_ENTRIES where SE_QA0FLAG = 'Pass'
and (SE_PROJECT_CODE like '%.S' or SE_PROJECT_CODE like '%.T' or SE_PROJECT_CODE like '%.A')
and SE_START >= to_date('2013-01-15 00:00:00','YYYY-MM-DD HH24:MI:SS')
order by  SE_START asc"""

try:
    conn = cx_Oracle.connect(databaseSCO)
    cursor = conn.cursor()
except Exception as e:
    print e
    sys.exit(1)

asdm = AsdmCheck()

rows = cursor.execute(sql)

for i in rows:
    asdm.setUID(i[0])
    scan = getScan(asdm.asdmDict['Scan'])
    field = getField(asdm.asdmDict['Field'])
    source = getSource(asdm.asdmDict['Source'])
    scan['target'] = scan.apply(lambda x: True if str(x['scanIntent']).find('OBSERVE_TARGET') > 0 else False ,axis = 1)
    targets = map(unicode.strip,list(scan[scan['target'] == True].sourceName.values))
    field['target'] = field.apply(lambda x: True if str(x['fieldName']).strip() in targets else False, axis = 1)
    source['target'] = source.apply(lambda x: True if str(x['sourceName']).strip() in targets else False, axis = 1)
    source['ra'], source['dec'] = zip(*source.apply(lambda x: arrayParser(x['direction'],1), axis = 1))
    field['ra'],field['dec'] = zip(*field.apply(lambda x: arrayParser(x['referenceDir'],2)[0], axis = 1))
    del source['spectralWindowId']
    source = source.drop_duplicates()
    source2 = source[source['target'] == True]
    field2 = field[field['target'] == True]
    merge = pd.merge(field2, source2, left_on='sourceId',right_on='sourceId',how='inner')
    merge['ra_diff'] = merge.apply(lambda x: pl.absolute(float(x['ra_x'])-float(x['ra_y'])), axis = 1)
    merge['dec_diff'] = merge.apply(lambda x: pl.absolute(float(x['dec_x'])-float(x['dec_y'])), axis = 1)
    merge['total'] = merge.apply(lambda x: ((x['ra_diff']**2 + x['dec_diff']**2)**(0.5))*206264.80624709636, axis = 1)
    if merge.total.describe()[7] > 1:
        print i[0]+'|'+i[1]+'|'+i[2]

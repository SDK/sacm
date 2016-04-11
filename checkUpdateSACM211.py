#!/bin/env python

import pandas as pd
import cx_Oracle
from sacm.password import *
import sys


try:
    conn = cx_Oracle.connect(databaseSCO)
    cursor = conn.cursor()
except Exception as e:
    print e
    sys.exit(1)



def checkDB(uid=None,cursor=None):
    sql = "select * from alma.xml_updates where asdm_uid = '%s' and elaboration like 'SACM-211'"%uid
    print sql
    try:
        cursor.execute(sql)
    except Exception as e:
        print e
        sys.exit(1)
    result = cursor.fetchall()
    if len(result) > 0:
        return True
    else:
        return False

image = pd.read_csv('releaseImage.txt',sep='|')
image['updated'] = image.apply(lambda x: checkDB(x['EB'], cursor) , axis = 1)
df = image[['CODE','SB','EB','updated']]

to_html = open('sacm211.html','w')
to_html.write('<html><head></head><body>'+df.to_html(index=False,escape=False)+'</body></html>')
to_html.close()

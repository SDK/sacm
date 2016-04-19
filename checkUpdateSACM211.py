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
    #print sql
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



arcs = pd.read_csv('arcs.csv',sep = ' ', header= None)
arcs.columns = ['all']
arcs['code'],arcs['arc'] = zip(*arcs.apply(lambda x: x['all'].split('\t') , axis = 1 ))
df = pd.merge(image,arcs,left_on='CODE',right_on='code',how='inner')
df1 = df[['CODE','arc','SB','EB','updated']]
to_html = open('sacm211.html','w')

to_html.write('<html><head></head><body>'+df1.to_html(index=False,escape=False)+'</body></html>')
to_html.close()

f = open('point_zero_one.csv', 'r')
g = list()
foo = f.readlines()
for idx, i in enumerate(foo):
    if 'uid' in i:
        g.append((foo[idx].replace('\n','').split(' ')[0], foo[idx].replace('\n','').split(' ')[1], foo[idx].replace('\n','').split(' ')[2], foo[idx+1].replace('Max.Offset error:','').replace('\n','').replace(' ','')))
df = pd.DataFrame(g, columns=['uid','sb','code','error'])
df['updated'] = df.apply(lambda x: checkDB(x['uid'], cursor) , axis = 1)
df = df.sort(['code'])
df = df.reset_index(drop=True)
df1 = df[['code','sb','uid','updated']]
to_html = open('sacm211-all.html','w')
to_html.write('<html><head></head><body>'+df1.to_html(index=False,escape=False)+'</body></html>')
to_html.close()
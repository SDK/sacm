__author__ = 'sagonzal'
from MetaData import *
import cx_Oracle
import sys
from password import databaseSCO as database
import pandas as pd
results = list()
sql = '''select * from (
select EXECBLOCKUID,starttime from ALMA.AQUA_EXECBLOCK where OBSPROJECTCODE not like '%CSV' order by STARTTIME desc)
where rownum <2'''
orcl = cx_Oracle.connect(database)
cursor = orcl.cursor()
cursor.execute(sql)


for uid in cursor:
    print uid[0],uid[1]
    try:
        tocheck = AsdmCheck()
        tocheck.setUID(uid[0])
    except Exception as e:
        print e
        print "Error at ASDM:", tocheck.uid

    results.append((tocheck.uid, uid[1], tocheck.isValidUID(), tocheck.isValidNullState(),
                    tocheck.isValidSyscaltimestamp(),tocheck.iscsv2555()))

df = pd.DataFrame(results)
df.columns = ['UID','DATE','ValidUID','NullState','SyscalTime','CSV2555']
df.to_html('metadata_result.html')
df.to_csv('metadata_result.csv')






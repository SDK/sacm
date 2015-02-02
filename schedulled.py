__author__ = 'sagonzal'
from MetaData import *
import cx_Oracle
from sacm.password import databaseSCO as database
results = list()
sql = '''select EXECBLOCKUID,starttime from ALMA.AQUA_EXECBLOCK where OBSPROJECTCODE not like '%CSV' order by STARTTIME desc'''
orcl = cx_Oracle.connect(database)
cursor = orcl.cursor()
cursor.execute(sql)

tocheck = AsdmCheck()
for uid in cursor:
    print uid[0],uid[1]
    try:
        tocheck.setUID(uid[0])
        tocheck.doCheck()
        tocheck.save()
    except Exception as e:
        print e
        print "Error at ASDM:", tocheck.uid
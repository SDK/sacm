__author__ = 'sagonzal'
from sacm.password import *
import sys
import os
import cx_Oracle
import subprocess

try:
    conn = cx_Oracle.connect(databaseSCO)
    cursor = conn.cursor()
except Exception as e:
    print e
    sys.exit(1)

sbUID = sys.argv[1]
if 'uid___' in sbUID:
    sbUID = sbUID.replace('___','://').replace('_','_')

sql = '''select se_eb_uid from ALMA.SHIFTLOG_ENTRIES where SE_SB_ID = "%s" and SE_QA0FLAG = "Pass"'''%sbUID

rows = cursor.execute(sql)
sbUID_norma = sbUID.replace('://','___').replace('/','_')

if rows > 0:
    os.mkdir(sbUID_norma)
    os.chdir(sbUID_norma)
    for i in rows:
        subprocess.Popen(['asdmExport','-m',i[0]])
    os.chdir('../')



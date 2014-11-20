__author__ = 'sagonzal'
from MetaData import *
import cx_Oracle
import sys
import pandas as pd
results = list()
sql = '''

'''


uid = 'uid://A002/X946a23/X9de'
try:
    tocheck = AsdmCheck()
    tocheck.setUID(uid)
except Exception as e:
    print e
    print "Error at ASDM:", tocheck.uid



results.append((tocheck.uid,tocheck.isValidUID(),tocheck.isNullState(),tocheck.isValidSyscaltimestamp(),tocheck.iscsv2555()))





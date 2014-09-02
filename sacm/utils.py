__author__ = 'sdk'
from time import strftime, gmtime, mktime
import datetime
from xml.dom import minidom
import numpy as np
import cx_Oracle
from password import databaseSCO

tables = {"ASDM": "XML_ASDM_ENTITIES", "Main": "XML_MAINTABLE_ENTITIES",
    "AlmaRadiometer": "XML_ALMARADIOMETERTAB_ENTITIES", "Antenna": "XML_ANTENNATABLE_ENTITIES",
    "CalAmpli": "XML_CALAMPLITABLE_ENTITIES", "CalAtmosphere": "XML_CALATMOSPHERETABL_ENTITIES",
    "CalCurve": "XML_CALCURVETABLE_ENTITIES", "CalSeeing": "XML_CALSEEINGTABLE_ENTITIES",
    "CalWVR": "XML_CALWVRTABLE_ENTITIES", "CalData": "XML_CALDATATABLE_ENTITIES",
    "CalDelay": "XML_CALDELAYTABLE_ENTITIES", "CalDevice": "XML_CALDEVICETABLE_ENTITIES",
    "CalFlux": "XML_CALFLUXTABLE_ENTITIES", "CalPhase": "XML_CALPHASETABLE_ENTITIES",
    "CalReduction": "XML_CALREDUCTIONTABLE_ENTITIES", "ConfigDescription": "XML_CONFIGDESCRIPTION_ENTITIES",
    "CorrelatorMode": "XML_CORRELATORMODETAB_ENTITIES", "DataDescription": "XML_DATADESCRIPTIONTA_ENTITIES",
    "ExecBlock": "XML_EXECBLOCKTABLE_ENTITIES", "Feed": "XML_FEEDTABLE_ENTITIES",
    "Annotation": "XML_ANNOTATIONTABLE_ENTITIES", "Ephemeris": "XML_EPHEMERISTABLE_ENTITIES",
    "Anotation": "XML_ANNOTATIONTABLE_ENTITIES", "CalBandpass": "XML_CALBANDPASSTABLE_ENTITIES",
    "CalPointing": "XML_CALPOINTINGTABLE_ENTITIES", "Field": "XML_FIELDTABLE_ENTITIES",
    "Flag": "XML_FLAGTABLE_ENTITIES", "Focus": "XML_FOCUSTABLE_ENTITIES",
    "FocusModel": "XML_FOCUSMODELTABLE_ENTITIES", "Pointing": "XML_POINTINGTABLE_ENTITIES",
    "PointingModel": "XML_POINTINGMODELTABL_ENTITIES", "Polarization": "XML_POLARIZATIONTABLE_ENTITIES",
    "Processor": "XML_PROCESSORTABLE_ENTITIES", "Receiver": "XML_RECEIVERTABLE_ENTITIES",
    "SBSummary": "XML_SBSUMMARYTABLE_ENTITIES", "Scan": "XML_SCANTABLE_ENTITIES",
    "Source": "XML_SOURCETABLE_ENTITIES", "SpectralWindow": "XML_SPECTRALWINDOWTAB_ENTITIES",
    "Ephemeris": "XML_EPHEMERISTABLE_ENTITIES", "State": "XML_STATETABLE_ENTITIES",
    "Station": "XML_STATIONTABLE_ENTITIES", "Subscan": "XML_SUBSCANTABLE_ENTITIES",
    "SquareLawDetector": "XML_SQUARELAWDETECTOR_ENTITIES", "SwitchCycle": "XML_SWITCHCYCLETABLE_ENTITIES",
    "SysCal": "XML_SYSCALTABLE_ENTITIES", "Weather": "XML_WEATHERTABLE_ENTITIES",
    "SchedBlock":"XML_SCHEDBLOCK_ENTITIES", "ObsProject":"XML_OBSPROJECT_ENTITIES"}

def sdmTimeString(number=None):
    """
    Convert a time value (as used by ASDM, i.e. MJD in nanoseconds) into a FITS type string.
    :param number:
    """
    st = number/1000000000L
    # decimal microseconds ...
    number = (number-st*1000000000L)/1000
    # number of seconds since 1970-01-01T00:00:00
    st = st-3506716800L
    return strftime("%Y-%m-%dT%H:%M:%S", gmtime(st))+(".%6.6d" % number)


def gtm(t=None):
    """
    Convert a time value (as used by ASDM, i.e. MJD in nanoseconds) into a FITS type string.
    :param t:
    """
    st = t-3506716800000000000L
    return st/1000000000L


def gtm2(number=None):
    """
    Convert a time value (as used by ASDM, i.e. MJD in nanoseconds) into a FITS type string.
    :param number:
    """
    st = number/1000000000L
    # decimal microseconds ...
    number = (number-st*1000000000L)/1000
    # number of seconds since 1970-01-01T00:00:00
    st = st-3506716800L
    return datetime.datetime.fromtimestamp(mktime(gmtime(st))).replace(microsecond=(number))


def RadianTo(num=None, unit=None):
    """

    :param num:
    :param unit:
    :return:
    """
    Deg = float(num)*180.0/np.pi
    if unit == 'dms':
        if Deg < 0:
            Deg = -Deg
            sign = '-'
        else:
            sign = '+'
        g = int(Deg)
        m = int((Deg-g)*60.)
        s = (Deg-g-m/60.)*3600.
        return sign+str(g)+":"+str(m)+":"+str('%5.2f' % s)
    if unit == 'hms':
        h = int(Deg/15.)
        m = int((Deg/15.-h)*60.)
        s = (Deg/15.-h-m/60.)*3600.
        return str(h)+":"+str(m)+":"+str('%5.2f' % s)


def arrayParser(line=None, dimensions=None):
    """

    :param line: String to be formated
    :param dimensions: dimensions of the array
    :return: a list, or a list of list 1D o 2D arrays, no support for 3D arrays yet
    """
    result = list()
    line = line.strip()
    if dimensions == 1:
        elements = line.split(' ')[1]
        splits = line.split(' ')[2:]
        for i in splits:
            result.append(i)
        if int(elements) == len(result):
            return result
        else:
            return False

    if dimensions == 2:
        rows = int(line.split(' ')[1])
        columns = int(line.split(' ')[2])
        splits = line.split(' ')[3:]
        for j in range(0, rows):
            temp = list()
            for i in range(0, columns):
                temp.append(splits[i+(j*columns)])
            result.append(temp)
        return result


def GetXML(archiveUID=None,table=None):
    """

    :param archiveUID: Archive UID
    :param table: Table
    :return: XML String
    """
    sqlXML = "select XMLType.GetClobVal(xml) from ALMA.XXXXYYY where archive_uid='ZZZZCCCC' "
    sqlXML = sqlXML.replace('XXXXYYY',tables[table]).replace('ZZZZCCCC',archiveUID)
    try:
        orcl = cx_Oracle.connect(databaseSCO)
        cursorXML = orcl.cursor()
        cursorXML.execute(sqlXML)
        XMLTable = cursorXML.fetchone()
        return XMLTable[0].read()
    except Exception as e:
        print e
        return False
    return False


def getProjectUID(projectCode=None):





###############################################################
#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# sagonzal :D

import cx_Oracle
import os
import sys
import pandas as pd
from load import *


deleted_sbs = list()

os.putenv('ORACLE_HOME', '/home/oracle/app/oracle/product/11.2.0/client_1')
os.putenv('LD_LIBRARY_PATH', '/home/oracle/app/oracle/product/11.2.0/client_1/lib')
os.environ['ORACLE_HOME'] = '/home/oracle/app/oracle/product/11.2.0/client_1'
os.environ['LD_LIBRARY_PATH'] = '/home/oracle/app/oracle/product/11.2.0/client_1/lib'

database = "almasu/alma4dba@oraosf.osf.alma.cl/OFFLINE.OSF.CL"
conn = cx_Oracle.connect(database)
cycle = 2
cycle_code = dict()
cycle_code[1] = '2012._.%._'
cycle_code[2] = '2013._.%._'
cycle_code[3] = '2014._.%._'

sb_list = list()
define_list = list()
spectral_list = list()

def getSBs(prj_uid=None):
    sql = '''with t1 as (
        select status_entity_id as seid1 from ALMA.OBS_UNIT_SET_STATUS where OBS_PROJECT_ID = 'PPPRRRJJJ' and PARENT_OBS_UNIT_SET_STATUS_ID is null
        ),
        t2 as (
        select  status_entity_id as seid2, PARENT_OBS_UNIT_SET_STATUS_ID as paid2, domain_entity_id  from ALMA.OBS_UNIT_SET_STATUS where OBS_PROJECT_ID = 'PPPRRRJJJ'
        ),
        t3 as (
        select  status_entity_id as seid3, PARENT_OBS_UNIT_SET_STATUS_ID as paid3 from ALMA.OBS_UNIT_SET_STATUS where OBS_PROJECT_ID = 'PPPRRRJJJ'
        ),
        t4 as (
        select  status_entity_id as seid4, PARENT_OBS_UNIT_SET_STATUS_ID as paid4 from ALMA.OBS_UNIT_SET_STATUS where OBS_PROJECT_ID = 'PPPRRRJJJ'
        ),
        t5 as (
        select  domain_entity_id as scheckblock_uid, PARENT_OBS_UNIT_SET_STATUS_ID as paid5 from ALMA.SCHED_BLOCK_STATUS where OBS_PROJECT_ID = 'PPPRRRJJJ'
        )
        SELECT t2.domain_entity_id, t5.scheckblock_uid
        FROM t1,
          t2,
          t3,
          t4,
          t5
        WHERE t1.seid1 = t2.paid2
        AND t2.seid2   = t3.paid3
        AND t3.seid3   = t4.paid4
        AND t4.seid4   = t5.paid5
        ORDER BY 1 ASC'''
    sql = sql.replace('PPPRRRJJJ', prj_uid)
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        sb = cursor.fetchall()
        return sb
    except Exception as e:
        print e


def spectrals_sb(prj_uid=None, partid=None):
    spectral_sql = '''with t1 as (
select status_entity_id as seid1 from ALMA.OBS_UNIT_SET_STATUS where OBS_PROJECT_ID = 'PPPRRRJJJ' and PARENT_OBS_UNIT_SET_STATUS_ID is null
),
t2 as (
select  status_entity_id as seid2, PARENT_OBS_UNIT_SET_STATUS_ID as paid2, domain_entity_id  from ALMA.OBS_UNIT_SET_STATUS where OBS_PROJECT_ID = 'PPPRRRJJJ'
),
t3 as (
select  status_entity_id as seid3, PARENT_OBS_UNIT_SET_STATUS_ID as paid3 from ALMA.OBS_UNIT_SET_STATUS where OBS_PROJECT_ID = 'PPPRRRJJJ'
),
t4 as (
select  status_entity_id as seid4, PARENT_OBS_UNIT_SET_STATUS_ID as paid4 from ALMA.OBS_UNIT_SET_STATUS where OBS_PROJECT_ID = 'PPPRRRJJJ'
),
t5 as (
select  domain_entity_id as scheckblock_uid, PARENT_OBS_UNIT_SET_STATUS_ID as paid5 from ALMA.SCHED_BLOCK_STATUS where OBS_PROJECT_ID = 'PPPRRRJJJ'
)
SELECT t2.domain_entity_id, t5.scheckblock_uid
FROM t1,
  t2,
  t3,
  t4,
  t5
WHERE t1.seid1 = t2.paid2
AND t2.seid2   = t3.paid3
AND t3.seid3   = t4.paid4
AND t4.seid4   = t5.paid5
AND t2.domain_entity_id = 'ZZZXXXYYY'
ORDER BY 1 ASC'''
    spectral_sql = spectral_sql.replace('PPPRRRJJJ', prj_uid).replace('ZZZXXXYYY', partid)
    try:
        cursor = conn.cursor()
        cursor.execute(spectral_sql)
        sb = cursor.fetchall()
        for i in sb:
            spectral_list.append((prj_uid,i[1],'SpectralScan'))
    except Exception as e:
        print e


def is_spectralscan(prj_uid=None):
    spectral_sql = '''select al1.archive_uid, x.*
        from
        ALMA.XML_OBSPROJECT_ENTITIES al1,
        XMLTable('for $first in /*:ObsProject/*:ObsProgram/*:ScienceGoal return element i {
                            element pol { data($first/*:SpectralSetupParameters/@polarisation)},
                            element type { data($first/*:SpectralSetupParameters/@type)},
                            element partid { data($first/*:ObsUnitSetRef/@partId)}
                        }'
             PASSING al1.XML COLUMNS
            pol varchar2(50) PATH 'pol',
            type varchar2(32) PATH 'type',
            partid varchar2(20) PATH 'partid'
            ) x
        where al1. archive_uid = 'XXXXYYYY'
        order by al1.timestamp desc'''
    spectral_sql = spectral_sql.replace('XXXXYYYY', prj_uid)
    try:
        cursor = conn.cursor()
        cursor.execute(spectral_sql)
        science_goals = cursor.fetchall()
        for i in science_goals:
            #print i
            if i[2] == 'scan':
                #print '##########################'
                #print i
                spectrals_sb(i[0],i[3])
    except Exception as e:
        print e



def is_band89(prj_uid=None):
    band89_sql = '''with t1 as (
select status_entity_id as seid1 from ALMA.OBS_UNIT_SET_STATUS where OBS_PROJECT_ID = 'XXXXYYYYZZZZ' and PARENT_OBS_UNIT_SET_STATUS_ID is null
),
t2 as (
select  status_entity_id as seid2, PARENT_OBS_UNIT_SET_STATUS_ID as paid2, domain_entity_id  from ALMA.OBS_UNIT_SET_STATUS where OBS_PROJECT_ID = 'XXXXYYYYZZZZ'
),
t3 as (
select  status_entity_id as seid3, PARENT_OBS_UNIT_SET_STATUS_ID as paid3 from ALMA.OBS_UNIT_SET_STATUS where OBS_PROJECT_ID = 'XXXXYYYYZZZZ'
),
t4 as (
select  status_entity_id as seid4, PARENT_OBS_UNIT_SET_STATUS_ID as paid4 from ALMA.OBS_UNIT_SET_STATUS where OBS_PROJECT_ID = 'XXXXYYYYZZZZ'
),
t5 as (
select  domain_entity_id as schedblock_uid, PARENT_OBS_UNIT_SET_STATUS_ID as paid5 from ALMA.SCHED_BLOCK_STATUS where OBS_PROJECT_ID = 'XXXXYYYYZZZZ'
),
t6 as (
select archive_uid as sb_uid, receiver_band as band from ALMA.BMMV_SCHEDBLOCK where prj_ref = 'XXXXYYYYZZZZ'
)
SELECT t2.domain_entity_id, t5.schedblock_uid,t6.band
FROM t1,
  t2,
  t3,
  t4,
  t5,
  t6
WHERE t1.seid1 = t2.paid2
AND t2.seid2   = t3.paid3
AND t3.seid3   = t4.paid4
AND t4.seid4   = t5.paid5
and t6.sb_uid = t5.schedblock_uid
ORDER BY 1 ASC'''
    band89_sql = band89_sql.replace('XXXXYYYYZZZZ',prj_uid)
    try:
        cursor = conn.cursor()
        cursor.execute(band89_sql)
        sb = cursor.fetchall()
        for i in sb:
            #print i
            if 'RB_08' in i[2]:
                sb_list.append((prj_uid,i[1],'Band8'))
            if 'RB_09' in i[2]:
                sb_list.append((prj_uid,i[1],'Band9'))

    except Exception as e:
        print e


def define_sbs(prj_uid=None):
    sbs = getSBs(prj_uid)
    basebands = pd.DataFrame()
    spectral = pd.DataFrame()
    targets = pd.DataFrame()
    science = pd.DataFrame()
    phase = pd.DataFrame()

    for i in sbs:
        a = getSBData(i[1])
        basebands = pd.concat([basebands,a[0]],ignore_index=True)
        spectral = pd.concat([spectral,a[1]],ignore_index=True)
        targets = pd.concat([targets,a[2]],ignore_index=True)
        phase = pd.concat([phase,a[3]],ignore_index=True)
        science = pd.concat([science,a[4]],ignore_index=True)

    a1 = pd.merge(phase,targets,how='inner', left_on = 0 , right_on = 1,left_index=True,copy=False)
    b1 = pd.merge(a1,spectral, left_on= '0_y', right_on= 0)
    b1 = b1[['3_y','0_y']]
    b1 = b1.drop_duplicates()
    b1 = b1.reset_index(drop=True)
    b1 = b1.T.groupby(level=0).first().T
    a = pd.merge(science,targets,how='inner', left_on = 0 , right_on = 1,left_index=True,copy=False)
    b = pd.merge(a,spectral, left_on= '0_y', right_on= 0)
    b = b[['3_y','0_y']]
    b = b.drop_duplicates()
    b = b.reset_index(drop=True)
    b = b.T.groupby(level=0).first().T

    for i in b.index:
        row = b.ix[i]
        if len(b1[b1['3_y'] == row['3_y']]) > 0:
            if len(b1[b1['0_y'] == row['0_y']]) > 0:
                define_list.append((prj_uid,row['3_y'],'Same Phase Setup'))
                #print prj_uid,row['3_y'], 'Pipeline Ready'
            else:
                define_list.append((prj_uid,row['3_y'],'Different Phase Setup'))
                #print prj_uid,row['3_y'], 'NOT Pipeline Ready'
        else:
            if deleted_sbs.count(row['3_y']) == 0:
                define_list.append((prj_uid,row['3_y'],'No Phase Cal found (TP?)'))
                #print prj_uid,row['3_y'], 'NOT Pipeline Ready (Total Power?)'
            else:
                define_list.append((prj_uid,row['3_y'],'Deleted'))
                #print prj_uid,row['3_y'], 'SB Deleted'

    return (a,b,a1,b1,science,targets,phase,spectral,basebands)

sql = '''select obs_project_id
from ALMA.OBS_PROJECT_STATUS
where obs_project_id in (select prj_archive_uid from ALMA.BMMV_OBSPROJECT where prj_code like 'XXXYYYZZZ')
and domain_entity_state in ('Ready', 'Canceled', 'InProgress', 'Broken','Completed', 'Repaired','Phase2Submitted')'''

sql = sql.replace('XXXYYYZZZ',cycle_code[int(cycle)])

sql1 = "select DOMAIN_ENTITY_ID from ALMA.SCHED_BLOCK_STATUS where DOMAIN_ENTITY_STATE = 'Deleted'"
cursor = conn.cursor()

cursor.execute(sql1)

for i in cursor:
    deleted_sbs.append(i[0])

sql2 = "select prj_archive_uid,prj_code from ALMA.BMMV_OBSPROJECT"

cursor.execute(sql2)

proj_code = dict()
for i in cursor:
    proj_code[i[0]] = i[1]

sql3 = "select DOMAIN_ENTITY_ID, PARENT_OBS_UNIT_SET_STATUS_ID from ALMA.SCHED_BLOCK_STATUS"

cursor.execute(sql3)

sb_mous = dict()
for i in cursor:
    sb_mous[i[0]] = i[1]

sql4 = "select archive_uid, sb_name from ALMA.BMMV_SCHEDBLOCK"

cursor.execute(sql4)

sb_name = dict()
for i in cursor:
    sb_name[i[0]] = i[1]

cursor.execute(sql)

for i in cursor:
    is_band89(i[0])
    is_spectralscan(i[0])
    define_sbs(i[0])

a = pd.DataFrame(sb_list)
b = pd.DataFrame(define_list)
c = pd.DataFrame(spectral_list)
d = pd.merge(b,a,left_on=1,right_on=1,how='left')
f = pd.merge(d,c,left_on=1,right_on=1,how='left')
f = f.drop_duplicates()
del f[0]
del f['0_y']

f = f.fillna('')
f['SB_NAME'] = f.apply(lambda x: sb_name[x[1]], axis=1)
f['MOUS'] = f.apply(lambda x: sb_mous[x[1]], axis=1)
f['PRJ_CODE'] = f.apply(lambda x: proj_code[x['0_x']], axis=1)
f['Pipeline'] = f.apply(lambda x: True if x['2_x'] == 'Same Phase Setup' else False, axis = 1)
f['Pipeline'] = f.apply(lambda x: False if 'Band' in x['2_y'] else x['Pipeline'] , axis = 1)
f =f[['PRJ_CODE','0_x','MOUS','SB_NAME',1,'Pipeline','2_x','2_y',2]]
f.columns = ['PRJ_CODE','PRJ_UID','MOUS','SB_NAME','SB_UID','Pipeline','PhaseSetup','BAND_8-9','SpectralScan']

to_html = open('pipeline.html','w')
to_html.write('<html><head></head><body>'+f.to_html()+'</body></html>')
to_html.close()

to_csv = open('pipeline.csv','w')
to_csv.write(f.to_csv(sep='\t'))
to_csv.close()






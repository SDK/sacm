__author__ = 'sdk'
from time import strftime, gmtime, mktime
import datetime
from xml.dom import minidom
import numpy as np
import cx_Oracle
from password import databaseSCO as database
import pandas as pd
pd.options.mode.chained_assignment = None

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
    "State": "XML_STATETABLE_ENTITIES", "Station": "XML_STATIONTABLE_ENTITIES", "Subscan": "XML_SUBSCANTABLE_ENTITIES",
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

def returnMAXPWVC(pwv=None):
    if pwv <= 0.472:
        return 0.472
    elif pwv <= 0.658:
        return 0.658
    elif pwv <= 0.913:
        return 0.913
    elif pwv <= 1.262:
        return 1.262
    elif pwv <= 1.796:
        return  1.796
    elif pwv <= 2.748:
        return 2.748
    else:
        return 5.186


def findChannel(start=None, width=None, repFreq=None, nchan=None):
    channel = 0
    if width < 0:
        for i in xrange(nchan):
            if start > repFreq:
                start = start + width
            else:
                channel = -1.*i
                break
    else:
        for i in xrange(nchan):
            if start < repFreq:
                start = start + width
            else:
                channel = i
                break

    return channel


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
        return sign+str(g)+":"+str(m)+":"+str('%5.5f' % s)
    if unit == 'hms':
        h = int(Deg/15.)
        m = int((Deg/15.-h)*60.)
        s = (Deg/15.-h-m/60.)*3600.
        return str(h)+":"+str(m)+":"+str('%5.5f' % s)


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
        orcl = cx_Oracle.connect(database)
        cursorXML = orcl.cursor()
        cursorXML.execute(sqlXML)
        XMLTable = cursorXML.fetchone()
        return XMLTable[0].read()
    except Exception as e:
        print e
        return False
    return False


def getProjectUID(projectCode=None):
    """

    :param projectCode:
    :return:
    """
    sql = "select prj_archive_uid from ALMA.BMMV_OBSPROJECT where prj_code = 'XXXYYY'"
    sql = sql.replace('XXXYYY',projectCode)
    try:
        orcl = cx_Oracle.connect(database)
        cursor = orcl.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        orcl.close()
        return data[0][0]

    except Exception as e:
        print e

def getSBMOUS():
    sql = "select DOMAIN_ENTITY_ID, PARENT_OBS_UNIT_SET_STATUS_ID from ALMA.SCHED_BLOCK_STATUS"
    try:
        orcl = cx_Oracle.connect(database)
        cursor = orcl.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        status = list()
        for i in data:
            status.append((i[0],i[1]))
        orcl.close()
        return status
    except Exception as e:
        print e

def getSBNames():
    sql = "select archive_uid, sb_name from ALMA.BMMV_SCHEDBLOCK"
    try:
        orcl = cx_Oracle.connect(database)
        cursor = orcl.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        sbnames = list()
        for i in data:
            sbnames.append((i[0],i[1]))
        orcl.close()
        return sbnames
    except Exception as e:
        print e

def getProjectCodes(cycle=2):
    cycle_code = dict()
    cycle_code[0] = '2011._.%._'
    cycle_code[1] = '2012._.%._'
    cycle_code[2] = '2013._.%._'
    cycle_code[3] = '2015._.%._'

    sql = '''select al2.PRJ_ARCHIVE_UID, al2.code
    from ALMA.OBS_PROJECT_STATUS al1,
    ALMA.BMMV_OBSPROJECT al2
    where al1.obs_project_id in (select prj_archive_uid from ALMA.BMMV_OBSPROJECT where prj_code like 'XXXYYYZZZ')
    and al1.domain_entity_state in ('Ready', 'Canceled', 'InProgress', 'Broken','Completed', 'Repaired','Phase2Submitted')
    and al1.OBS_PROJECT_ID = al2.PRJ_ARCHIVE_UID '''

    sql = sql.replace('XXXYYYZZZ',cycle_code[int(cycle)])
    try:
        orcl = cx_Oracle.connect(database)
        cursor = orcl.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        codes = list()
        for i in data:
            codes.append((i[0],i[1]))
        orcl.close()
        return codes
    except Exception as e:
        print e



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
        orcl = cx_Oracle.connect(database)
        cursor = orcl.cursor()
        cursor.execute(sql)
        sb = cursor.fetchall()
        orcl.close()
        return sb
    except Exception as e:
        orcl.close()
        print e


def spectrals_sb(prj_uid=None, partid=None):
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
AND t2.domain_entity_id = 'ZZZXXXYYY'
ORDER BY 1 ASC'''
    sql = sql.replace('PPPRRRJJJ', prj_uid).replace('ZZZXXXYYY', partid)
    try:
        orcl = cx_Oracle.connect(database)
        cursor = orcl.cursor()
        cursor.execute(sql)
        sb = cursor.fetchall()
        specscan = list()
        for i in sb:
            specscan.append((prj_uid,i[1],'SpectralScan'))
        return specscan
    except Exception as e:
        print e


def is_spectralscan(prj_uid=None):
    sql = '''select al1.archive_uid, x.*
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
    sql = sql.replace('XXXXYYYY', prj_uid)
    try:
        orcl = cx_Oracle.connect(database)
        cursor = orcl.cursor()
        cursor.execute(sql)
        science_goals = cursor.fetchall()
        cursor.close()
        return science_goals
    except Exception as e:
        print e



def is_band89(prj_uid=None):
    sql = '''with t1 as (
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
    sql = sql.replace('XXXXYYYYZZZZ',prj_uid)
    try:
        orcl = cx_Oracle.connect(database)
        cursor = orcl.cursor()
        cursor.execute(sql)
        sb = cursor.fetchall()
        cursor.close()
        return sb
    except Exception as e:
        print e





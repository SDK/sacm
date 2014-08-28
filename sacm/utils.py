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








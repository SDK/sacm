__author__ = 'sdk'
from time import strftime, gmtime
from xml.dom import minidom
import numpy as np

def sdmTimeString(number):
    """
    Convert a time value (as used by ASDM, i.e. MJD in nanoseconds) into a FITS type string.
    """
    st = number/1000000000L
    # decimal microseconds ...
    number=(number-st*1000000000L)/1000
    # number of seconds since 1970-01-01T00:00:00
    st = st-3506716800L
    return strftime("%Y-%m-%dT%H:%M:%S",gmtime(st))+(".%6.6d" % number)

def gtm(t = None):
    """
    Convert a time value (as used by ASDM, i.e. MJD in nanoseconds) into a FITS type string.
    """
    st = t-3506716800000000000L
    return st/1000000L


def RadianTo(num, unit):
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

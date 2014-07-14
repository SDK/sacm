__author__ = 'sdk'
from time import strftime, gmtime
from xml.dom import minidom
import numpy as np


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
    return st/1000000L


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







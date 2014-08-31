__author__ = 'sagonzal'
from checker import *
import pylab as mypl
import math as mymath

uid = 'uid://A002/X899169/X1179'


class asdmCheck:
    uid = ''
    asdmDict = dict()

    def setUID(self,uid=None):
        self.uid = uid
        return True


    def init(self):
        asdmList, asdm = getASDM(self.uid)
        for i in asdmList:
            self.asdmDict[i[0].strip()] = i[3].strip()


    def isNullState(self):
        main = getMain(self.asdmDict['Main'])
        main['null'] = main.apply(lambda x: True if 'null' in x['stateId'] else False, axis = 1)
        if len(main['null'].unique()) > 1:
            return True
        else:
            return False


    def isValidUID(self):
        for k,v in self.asdmDict.iteritems():
            if '/X0/X0/X0' in v:
                return True
        return False


    def isValidSyscaltimestamp(self):
        syscal = getSysCal(self.asdmDict['SysCal'])
        dfa = syscal[['spectralWindowId','antennaId','timeInterval']]
        spw = dfa.groupby('spectralWindowId')
        for name,group in spw:
            df = group
            df['time'] = df.apply(lambda x: int(x['timeInterval'].strip().split(' ')[0]) / 1000000000.0, axis = 1 )
            df['interval'] = df.apply(lambda x: int(x['timeInterval'].strip().split(' ')[1]) / 1000000000.0, axis = 1 )
            df['timestamp'] = df.apply(lambda x: x.time - x.interval / 2, axis = 1)
            t0 = 86400.0 * mymath.floor(df.timestamp.min() / 86400.0)
            df['utimes'] = df.apply(lambda x: x['time'] - t0, axis =1)
            nT = df.utimes.nunique()
            df['utimestamp'] = df.apply(lambda x: mypl.floor(x['timestamp']) - t0 , axis =1)
            nTS = df.utimestamp.nunique()
            print name,nT, nTS
            if nT != nTS:
                return False
        return True

    def iscsv2555(self):
        source = getSource(self.asdmDict['Source'])
        field = getField(self.asdmDict['Field'])
        src = source[['sourceId', 'sourceName']]
        src = src.drop_duplicates()
        fld = field[['sourceId', 'fieldName']]
        fld = fld.drop_duplicates()


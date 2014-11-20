__author__ = 'sagonzal'
from checker import *
import pylab as mypl
import math as mymath

uid = 'uid://A002/X899169/X1179'


class AsdmCheck:
    """

    """
    uid = ''
    asdmDict = dict()


    def setUID(self,uid=None):
        self.uid = uid
        asdmList, asdm = getASDM(self.uid)
        for i in asdmList:
            self.asdmDict[i[0].strip()] = i[3].strip()
        return True



    def isValidNullState(self):
        """


        :return:
        """
        try:
            main = getMain(self.asdmDict['Main'])
            main['null'] = main.apply(lambda x: True if 'null' in x['stateId'] else False, axis = 1)
            if len(main['null'].unique()) > 1:
                return False
            else:
                return True
        except Exception as e:
            return False
            pass



    def isValidUID(self):
        import re
        regex = re.compile("^uid\:\/\/A00.\/X[a-zA-Z0-9]+\/X[a-zA-Z0-9]+")
        for k,v in self.asdmDict.iteritems():
            if '/X0/X0/X0' in v:
                return False
            if regex.match(v) is None:
                return False
        return True


    def isValidSyscaltimestamp(self):
        try:
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
        except Exception as e:
            return False
            pass


    def iscsv2555(self):
        try:
            source = getSource(self.asdmDict['Source'])
            field = getField(self.asdmDict['Field'])
            src = source[['sourceId', 'sourceName']]
            src['sourceName1'] = src.apply(lambda x: x['sourceName'].strip(), axis = 1)
            src = src.drop_duplicates()
            fld = field[['sourceId', 'fieldName']]
            fld['fieldName1'] = fld.apply(lambda x: x['fieldName'].strip(), axis = 1)
            fld = fld.drop_duplicates()
            a = pd.merge(src,fld,left_on = 'sourceId',right_on='sourceId',how='outer')
            a['csv2555'] = a.apply(lambda x: True if x['sourceName1'] == x['fieldName1'] else False, axis = 1)
            if a['csv2555'].nunique() == 1 and a['csv2555'].unique()[0] is True:
                return True
            else:
                return False
        except Exception as e:
            return False



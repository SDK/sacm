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
    check = dict()



    def setUID(self,uid=None):
        self.uid = uid
        try:
            asdmList, asdm = getASDM(self.uid)
            for i in asdmList:
                self.asdmDict[i[0].strip()] = i[3].strip()
            return True
        except Exception as e:
            print 'There is a problem with the uid: ', uid
            print e


    def isValidNullState(self):
        """
        Checks the Main.xml table for "null" states
        Sets in the self.check dictionary the value 'NullState' with True or False
        True: There is no state with null values
        False: There is at least one state in the Main.xml table with null state.

        :return:
        """
        try:
            main = getMain(self.asdmDict['Main'])
            main['null'] = main.apply(lambda x: True if 'null' in x['stateId'] else False, axis = 1)
            if len(main['null'].unique()) > 1:
                self.check['NullState'] = True
            else:
                self.check['NullState'] = False
        except Exception as e:
            return e
        return True


    def isValidUID(self):
        """

        :return:
        """
        import re
        regex = re.compile("^uid\:\/\/A00.\/X[a-zA-Z0-9]+\/X[a-zA-Z0-9]+")
        try:
            for k,v in self.asdmDict.iteritems():
                if '/X0/X0/X0' in v:
                    self.check['ValidUID'] = True
                    return True
                if regex.match(v) is None:
                    self.check['ValidUID'] = True
                    return True
            self.check['ValidUID'] = False
            return True
        except Exception as e:
            print e
            return False

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
                #print name,nT, nTS
                if nT != nTS:
                    self.check['SysCalTimes'] = False
                    return True
            self.check['SysCalTimes'] = True
            return True
        except Exception as e:
            return False


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
                self.check['CSV2555'] = False
            else:
                self.check['CSV2555'] = True
            return True
        except Exception as e:
            return False


    def isfixplanets(self):
        try:
            source = getSource(self.asdmDict['Source'])
            df = source[['sourceName','direction']].drop_duplicates()
            df['coordinate'] = df.apply(lambda x: True if float(arrayParser(x['direction'].strip() , 1 )[0]) == 0.0 else False , axis = 1)
            df['coordinate2'] = df.apply(lambda x: True if float(arrayParser(x['direction'].strip() , 1 )[1]) == 0.0 else False , axis = 1)
            if df['coordinate'].unique()[0] is False and df['coordinate'].nunique() == 1 and df['coordinate2'].unique()[0] is False and df['coordinate2'].nunique() == 1:
                self.check['FixPlanets'] = False
            else:
                self.check['FixPlanets'] = True
            return True
        except Exception as e:
            return False

    def doCheck(self):
        self.iscsv2555()
        self.isValidSyscaltimestamp()
        self.isValidUID()
        self.isfixplanets()
        self.isValidNullState()


    def save(self):
        pass






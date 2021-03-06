__author__ = 'sagonzal'
from checker import *
import pylab as mypl
import math as mymath
import itertools

class AsdmCheck:
    """

    """
    uid = ''
    asdmDict = dict()
    check = dict()
    toc = ''




    def setUID(self,uid=None):
        self.uid = uid
        try:
            asdmList, asdm , self.toc = getASDM(self.uid)
            for i in asdmList:
                self.asdmDict[i[0].strip()] = i[3].strip()
            return True
        except Exception as e:
            print 'There is a problem with the uid: ', uid
            print e


    def isNullState(self):
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
                self.check['NullState'] = False
            else:
                self.check['NullState'] = True
        except Exception as e:
            print e
            return False
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
                    self.check['ValidUID'] = False
                    return True
                if regex.match(v) is None:
                    self.check['ValidUID'] = False
                    return True
            self.check['ValidUID'] = True
            return True
        except Exception as e:
            print e
            return False

    def isSyscaltimestamp(self):
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
                #print (group)
                if nT != nTS:
                    self.check['SysCalTimes'] = True
                    return True
            self.check['SysCalTimes'] = False
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
                self.check['CSV2555'] = True
            else:
                self.check['CSV2555'] = False
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
                self.check['FixPlanets'] = True
            else:
                self.check['FixPlanets'] = False
            return True
        except Exception as e:
            return False

    def ict4871(self):
        try:
            ant = getAntennas(self.asdmDict['Antenna'])
            nant = ant.antennaId.nunique()
            syscal = getSysCal(self.asdmDict['SysCal'])
            sys_nant = syscal.antennaId.nunique()
            scan = getScan(self.asdmDict['Scan'])
            sc = scan[['scanNumber','startTime','scanIntent']]
            problem_list = list()
            if nant == sys_nant:
                df = syscal[['timeInterval','antennaId','spectralWindowId']]
                df['start'] = df.apply(lambda x: int(x['timeInterval'].strip().split(' ')[0]) - int(x['timeInterval'].strip().split(' ')[1])/2, axis = 1)
                df2 = pd.merge (df,sc, left_on='start',right_on='startTime',copy=False,how='inner')
                antlist = [x.strip(' ') for x in ant.antennaId.unique().tolist()]
                df3 = df2.groupby(['antennaId','spectralWindowId','scanNumber'])
                spw_list = syscal.spectralWindowId.unique().tolist()
                scan_list = df2.scanNumber.unique().tolist()
                fu = list(itertools.product(antlist,spw_list,scan_list))
                for i in fu:
                    try:
                        df3.groups[i]
                    except KeyError as k:
                        problem_list.append(i)

                if len(problem_list) > 0:
                    df = pd.DataFrame(problem_list, columns= ['antennaId','spectralWindowId','scanNumber'])
                    popular_scan = df.scanNumber.mode().values[0]
                    antennas = df.antennaId.nunique()
                    self.check['MissingTsys'] = False
                    self.check['MissingTsys_explain'] = 'Scan: '+str(popular_scan)+' Antennas Affected: '+str(antennas)
                else:
                    self.check['MissingTsys'] = True

            else:
                self.check['AntennasMissing'] = "Number of antennas are diferent between Antenna.xml ("+nant+") and SysCal.xml ("+sys_nant+")"
                self.check['MissingTsys'] = False
                self.check['MissingTsys_explain'] = 'Some antenna is completly missing from Syscal.xml table'


        except Exception as e:
            print e
            return False

    def doCheck(self):
        self.iscsv2555()
        self.isSyscaltimestamp()
        self.isValidUID()
        self.isfixplanets()
        self.isNullState()
        self.ict4871()



    def save(self):
        if len(self.check) != 0:
            sql = "select * from public.metadata where asdm_uid ='"+self.uid+"'"
            pgcursor.execute(sql)
            row = pgcursor.fetchone()
            if self.check['SysCalTimes'] and self.check['ValidUID'] and self.check['CSV2555'] and self.check['FixPlanets'] and self.check['NullState']:
                overall = True
            else:
                overall = False
            #print row
            if row is not None:
                print "ASDM: %s exist. UPDATING" % self.uid
                try:
                    pgcursor.execute("""UPDATE public.metadata set "check" = %s,
                                        syscal_time = %s,
                                        valid_uid = %s,
                                        csv2555 = %s,
                                        fixplanet = %s,
                                        null_state = %s,
                                        udate = %s
                                        where asdm_uid = %s;""",
                        ( overall, self.check['SysCalTimes'], self.check['ValidUID'], self.check['CSV2555'],
                          self.check['FixPlanets'],self.check['NullState'],datetime.datetime.now (),self.uid,))
                    pgconn.commit()
                except Exception as e:
                    print e
                    pass
            else:
                print "ASDM: %s exist. INSERTING" % self.uid
                try:
                    pgcursor.execute("""INSERT INTO "public"."metadata" ("asdm_uid","check","syscal_time","valid_uid","csv2555","fixplanet","null_state","cdate","udate","time_of_creation")
                                 values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                                 (self.uid, overall, self.check['SysCalTimes'], self.check['ValidUID'], self.check['CSV2555'],
                                  self.check['FixPlanets'],self.check['NullState'],datetime.datetime.now (),datetime.datetime.now (),self.toc))
                    pgconn.commit()
                except Exception as e:
                    print e
                    pass
        else:
            print "Run docheck() before save"
            pass







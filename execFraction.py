__author__ = 'sagonzal'
from MetaData import *
import pandas as pd
import sys
import Sensitivity.sensitivity as sensitivity
##############################

configDir = '/home/sagonzal/druva/PycharmProjects/MetaData/Sensitivity'
try:
    asdmUID = sys.argv[1]
    asdm = AsdmCheck()
    asdm.setUID(asdmUID)
    sb = getSBSummary(asdm.asdmDict['SBSummary'])
except Exception as e:
    print e
    sys.exit(1)

c3 = datetime.datetime(2015,10,1,0,0,0)
c2 = datetime.datetime(2014,6,3,0,0,0)
c1 = datetime.datetime(2013,10,12,0,0,0)

if asdm.toc >= c3:
    NAntOT = 36.
    cycle = 'Cycle 3'
elif asdm.toc >= c2:
    NAntOT = 34.
    cycle = 'Cycle 2'
elif asdm.toc >= c1:
    NAntOT = 32.
    cycle = 'Cycle 1'
else:
    NAntOT = 14.
    cycle = 'Cycle 0'

############################
sbUID = sb.values[0][0]
freq = float(sb.values[0][3])*1e9
band = sb.values[0][4]

for i in sb.values[0][6].split('"'):
    if i.find('maxPWVC') >= 0: maxPWV = float(i.split('=')[1].split(' ')[1])

maxPWV = returnMAXPWVC(maxPWV)


print sbUID

science = getSBScience(sbUID)
field = getSBFields(sbUID)
target = getSBTargets(sbUID)

df1 = pd.merge(science,target, left_on='entityPartId',right_on='ObsParameter',how='inner')
df2 = pd.merge(df1,field,left_on='FieldSource',right_on='entityPartId',how='inner')

dec = float(df2['latitude'].values[0])
ToSOT = float(df2['integrationTime'].values[0])
###############################

#############################

s = sensitivity.SensitivityCalculator(config_dir=configDir)
result =  s.calcSensitivity(maxPWV,freq,dec=dec,latitude=-23.029, N=NAntOT, BW=7.5e9, mode='image', N_pol=2,returnFull=True)
TsysOT = result['Tsys']

################################
ant = getAntennas(asdm.asdmDict['Antenna'])
NantEB = float(ant.antennaId.count())


################################
scan = getScan(asdm.asdmDict['Scan'])
scan['target'] = scan.apply(lambda x: True if str(x['scanIntent']).find('OBSERVE_TARGET') > 0 else False ,axis = 1)
scan['delta'] = scan.apply(lambda x:  (gtm2(x['endTime']) - gtm2(x['startTime'])).total_seconds() ,axis = 1)

target = list(scan[scan['target'] == True]['sourceName'].unique())
scan['atm'] = scan.apply(lambda x: True if str(x['scanIntent']).find('CALIBRATE_ATMOSPHERE') > 0 and x['sourceName'] in target else False,axis =1 )

ToSEB = float(scan['delta'][scan['target'] == True].sum())


################################
syscal = getSysCal (asdm.asdmDict['SysCal'])
syscal['startTime'] = syscal.apply(lambda x: int(x['timeInterval'].split(' ')[1]) - int(x['timeInterval'].split(' ')[2])/2 ,axis=1 )


###################################
spw = getSpectralWindow(asdm.asdmDict['SpectralWindow'])
spw['repWindow'] = spw.apply(lambda x: findChannel(float(x['chanFreqStart']),float(x['chanFreqStep']), freq, int(x['numChan'])), axis = 1)



################################


df1 = syscal[syscal['startTime'].isin(scan[scan['atm'] == True]['startTime'])]
df2 = df1[df1['spectralWindowId'] == spw[spw['repWindow'] != 0]['spectralWindowId'].values[0].strip()]
channel = int(spw[spw['repWindow'] != 0]['repWindow'].values[0])

if channel < 0:
    channel+=128

data = df2.apply(lambda x: arrayParser(x['tsysSpectrum'],2), axis = 1)
data2 = pd.DataFrame (data)
data2.columns = ['hola']
x = pd.concat([pd.DataFrame(v,index=np.repeat(k,len(v))) for k,v in data2.hola.to_dict().items()])
x = x.convert_objects(convert_numeric=True)


TsysEB = x[channel].median()

result = {'TimeOnSource_EB':ToSEB,
              'TimeOnSource_OT':ToSOT,
              'Tsys_OT':TsysOT,
              'Tsys_EB':TsysEB,
              'NAntennas_EB':NantEB,
              'NAntennas_OT': NAntOT,
              'Channel': channel}

execFrac = ((TsysOT/TsysEB)**2)*((NantEB*(NantEB-1.))/(NAntOT*(NAntOT-1.)))*(ToSEB/ToSOT)

print 'Executional Fraction: ', execFrac
print cycle
print 'Details:'
print result



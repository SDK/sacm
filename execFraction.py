__author__ = 'sagonzal'
from MetaData import *
import pandas as pd
import sys
import Sensitivity.sensitivity as sensitivity



NAntOT = 36
configDir = '/home/sagonzal/druva/PycharmProjects/MetaData/Sensitivity'
try:
    asdmUID = sys.argv[1]
    asdm = AsdmCheck()
    asdm.setUID(asdmUID)
    sb = getSBSummary(asdm.asdmDict['SBSummary'])
except Exception as e:
    print e
    sys.exit(1)


sbUID = sb.values[0][0]
freq = float(sb.values[0][3])*1e9
band = sb.values[0][4]

for i in sb.values[0][6].split('"'):
    if i.find('maxPWVC') >= 0: maxPWV = float(i.split('=')[1].split(' ')[1])


science = getSBScience(sbUID)
field = getSBFields(sbUID)
target = getSBTargets(sbUID)

df1 = pd.merge(science,target, left_on='entityPartId',right_on='ObsParameter',how='inner')
df2 = pd.merge(df1,field,left_on='FieldSource',right_on='entityPartId',how='inner')

dec = float(df2['latitude'].values[0])
ToSOT = float(df2['integrationTime'].values[0])


s = sensitivity.SensitivityCalculator(config_dir=configDir)



result =  s.calcSensitivity(maxPWV,freq,dec=dec,latitude=-23.029, N=NAntOT, BW=7.5e9, mode='image', N_pol=2,returnFull=True)

TsysOT = result['Tsys']

ant = getAntennas(asdm.asdmDict['Antenna'])
NantEB = ant.antennaId.count()

scan = getScan(asdm.asdmDict['Scan'])
scan['target'] = scan.apply(lambda x: True if str(x['scanIntent']).find('OBSERVE_TARGET') > 0 else False ,axis = 1)
scan['delta'] = scan.apply(lambda x:  (gtm2(x['endTime']) - gtm2(x['startTime'])).total_seconds() ,axis = 1)

ToSEB = float(scan['delta'][scan['target'] == True].sum())

print ToSEB,ToSOT,TsysOT,NantEB




__author__ = 'sagonzal'
from MetaData import *
import ASDM
from asdmTypes import *
from ASDM import *
from Pointing import *
from ASDMParseOptions import *
from sys import argv
from sys import stdout
import ephem
import sacm.geo_helper as gh
import matplotlib.pyplot as plt
plt.style.use('ggplot')

J0 = ephem.julian_date(0)

def azelToRaDec(az=None, el=None,lat=None,lon=None,alt=None, ut=None):
    global J0
    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lon)
    observer.elevation = alt
    observer.date = ut - J0
    return observer.radec_of(az, el)

parser = ASDMParseOptions()
parser.asALMA()
parser.loadTablesOnDemand(True)
# Read ASDM
asdmtable = ASDM()
if len(argv) == 1:
    asdmdir = 'uid___A002_X9f9284_X175e'
else:
    asdmdir = argv[1]

asdmtable.setFromFile(asdmdir, parser)
uid = asdmtable.entity().toString().split('"')[1]
asdm = AsdmCheck()
asdm.setUID(uid)
sb = getSBSummary(asdm.asdmDict['SBSummary'])

#Get all the Parts that we need
scan = getScan(asdm.asdmDict['Scan'])
subscan = getSubScan(asdm.asdmDict['Subscan'])
field = getField(asdm.asdmDict['Field'])
antenna = getAntennas(asdm.asdmDict['Antenna'])
station = getStation(asdm.asdmDict['Station'])
source = getSource(asdm.asdmDict['Source'])
sbUID = sb.values[0][0]



rows = asdmtable.pointingTable().get()
pointingList = list()
for idx,row in enumerate(rows):
    pointingList.append((idx, str(row.antennaId()), float(row.numSample()), float(row.numTerm()),str(row.timeInterval()), str(row.timeOrigin())))

pointing = pd.DataFrame(pointingList,columns = ['rowNum','antennaId','samples','iter','duration','origin'])


#do some transformations for matching the data
scan['target'] = scan.apply(lambda x: True if str(x['scanIntent']).find('OBSERVE_TARGET') > 0 else False ,axis = 1)
targets = map(unicode.strip,list(scan[scan['target'] == True].sourceName.values))

source['target'] = source.apply(lambda x: True if str(x['sourceName']).strip() in targets else False, axis = 1)
source['ra'], source['dec'] = zip(*source.apply(lambda x: arrayParser(x['direction'],1), axis = 1))
field['target'] = field.apply(lambda x: True if str(x['fieldName']).strip() in targets else False, axis = 1)

pointing['start'] = pointing.apply(lambda x: x['origin'][0:19], axis = 1)
foo = list(scan.scanNumber[scan['target'] == True])
mosaic = subscan.loc[subscan['scanNumber'].isin(foo) ]
mosaic['start'] = mosaic.apply(lambda x: sdmTimeString(x['startTime'])[0:19], axis = 1)


joined = pd.merge(mosaic,pointing,left_on='start',right_on='start',how='inner')
ra = float(source[source['target'] ==True]['ra'].unique()[0])
dec = float(source[source['target'] ==True]['dec'].unique()[0])
geo = pd.merge(antenna,station, left_on='stationId', right_on = 'stationId', how = 'inner')
geo['pos'] = geo.apply(lambda x: arrayParser(x['position'],1) , axis = 1 )
geo['lat'], geo['lon'], geo['alt'] = zip(*geo.apply(lambda x: gh.turn_xyz_into_llh(float(x.pos[0]),float(x.pos[1]),float(x.pos[2]), 'wgs84'),axis=1))
field['ra'],field['dec'] = zip(*field.apply(lambda x: arrayParser(x['referenceDir'],2)[0], axis = 1))

#TODO: Fix to match any antenna

correctedList = list()
correctedList.append((ra,dec))
for i in joined.query("antennaId == 'Antenna_1' and subscanIntent == 'ON_SOURCE'").rowNum.values:
    row  = rows[i]
    raOffset,decOffset = [[float(str(p[0]).replace('rad','').replace(',','.')),float(str(p[1]).replace('rad','').replace(',','.'))] for p in row.sourceOffset() ][0]
    correctedList.append((raOffset+ra, decOffset+dec))

corrected = pd.DataFrame(correctedList, columns=['ra','dec'])
corrected['series'] = 'Corrected'
corrected = corrected.drop_duplicates()
observed = field[field['target'] == True][['ra','dec']]
observed['series'] = 'Observed'
observed.ra.astype(float)
observed.dec.astype(float)

final = pd.concat([corrected,observed])
final[['ra','dec']] =  final[['ra','dec']].astype(float)
sboffset = getSBOffsets(sbUID)
sb = getSBSummary(asdm.asdmDict['SBSummary'])
sbUID = sb.values[0][0]


target = getSBTargets(sbUID)
science = getSBScience(sbUID)
partId =  target[target['ObsParameter'] == science.entityPartId.values[0]].FieldSource.values[0]

predicted = sboffset[sboffset['partId'] == partId][['latitude','longitude']]

predicted[['latitude','longitude']] = predicted[['latitude','longitude']].astype(float)

groups = final.groupby('series')

fig, ax = plt.subplots()
ax.margins(0.05)
for name, group in groups:
    ax.plot(group.ra, group.dec, marker='.', linestyle='', ms=12, label=name, alpha=0.7)

ax.legend()
plt.show()


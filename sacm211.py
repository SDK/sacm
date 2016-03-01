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
import dateutil.parser as prs
import math
import pylab as pl
pd.options.display.width = 300

J0 = ephem.julian_date(0)

def azelToRaDec(az=None, el=None,lat=None,lon=None,alt=None, ut=None):
    global J0
    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lon)
    observer.elevation = alt
    observer.date = ut - J0
    return observer.radec_of(az, el)

def measure(lat1, lon1, lat2, lon2):
    R = 6378.137 # Radius of earth in KM
    dLat = (lat2 - lat1) * np.pi / 180.
    dLon = (lon2 - lon1) * np.pi / 180.
    a = math.sin(dLat/2.) * math.sin(dLat/2.) + math.cos(lat1 * np.pi / 180.) * math.cos(lat2 * np.pi / 180.) * math.sin(dLon/2.) * math.sin(dLon/2.)
    c = 2. * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c
    return d * 1000. # meters

def rot(Pl, rLong, rLat):
    return [pl.cos(rLong)*pl.cos(rLat) * Pl[0] - pl.sin(rLong) * Pl[1] - pl.cos(rLong)*pl.sin(rLat) * Pl[2],
           pl.sin(rLong)*pl.cos(rLat) * Pl[0] + pl.cos(rLong) * Pl[1] - pl.sin(rLong)*pl.sin(rLat) * Pl[2],
           pl.sin(rLat) * Pl[0] + pl.cos(rLat) * Pl[2]]

parser = ASDMParseOptions()
parser.asALMA()
parser.loadTablesOnDemand(True)
# Read ASDM
asdmtable = ASDM()
if len(argv) == 1:
    asdmdir = 'uid___A002_Xaebbcb_X6ad'
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
sbfield = getSBFields(sbUID)


rows = asdmtable.pointingTable().get()
pointingList = list()
for idx,row in enumerate(rows):
    pointingList.append((idx, str(row.antennaId()), float(row.numSample()), float(row.numTerm()),str(row.timeInterval()), str(row.timeOrigin())))

pointingAll = pd.DataFrame(pointingList,columns = ['rowNum','antennaId','samples','iter','duration','origin'])

#TODO: Fix to match any antenna
pointing = pointingAll[pointingAll['antennaId'] == 'Antenna_1']

#do some transformations for matching the data
scan['target'] = scan.apply(lambda x: True if str(x['scanIntent']).find('OBSERVE_TARGET') > 0 else False ,axis = 1)
targets = map(unicode.strip,list(scan[scan['target'] == True].sourceName.values))

source['target'] = source.apply(lambda x: True if str(x['sourceName']).strip() in targets else False, axis = 1)
source['ra'], source['dec'] = zip(*source.apply(lambda x: arrayParser(x['direction'],1), axis = 1))
field['target'] = field.apply(lambda x: True if str(x['fieldName']).strip() in targets else False, axis = 1)

foo = list(scan.scanNumber[scan['target'] == True])
pointing['go'] = False
for i in subscan.loc[subscan['scanNumber'].isin(foo) ][['startTime','endTime']].values:
    pointing['go'] = pointing.apply(lambda x: True if  prs.parse(sdmTimeString(i[0])) - datetime.timedelta(seconds=1) <= prs.parse(x['origin']) and prs.parse(sdmTimeString(i[1])) >= prs.parse(x['origin']) else x['go'], axis = 1)

ra = float(source[source['target'] ==True]['ra'].unique()[0])
if ra < 0:
    ra = ra * -1.

dec = float(source[source['target'] ==True]['dec'].unique()[0])
geo = pd.merge(antenna,station, left_on='stationId', right_on = 'stationId', how = 'inner')
geo['pos'] = geo.apply(lambda x: arrayParser(x['position'],1) , axis = 1 )
geo['lat'], geo['lon'], geo['alt'] = zip(*geo.apply(lambda x: gh.turn_xyz_into_llh(float(x.pos[0]),float(x.pos[1]),float(x.pos[2]), 'wgs84'),axis=1))
field['ra'],field['dec'] = zip(*field.apply(lambda x: arrayParser(x['referenceDir'],2)[0], axis = 1))


correctedList = list()
correctedList.append((ra,dec,0))
for i in pointing.query('go == True').rowNum.values:
    row  = rows[i]
    raOffset,decOffset = [[float(str(p[0]).replace('rad','').replace(',','.')),float(str(p[1]).replace('rad','').replace(',','.'))] for p in row.sourceOffset() ][row.numSample()/2]
    correctedList.append((raOffset+ra, decOffset+dec, i))

correctedAll = pd.DataFrame(correctedList, columns=['ra','dec', 'row'])
corrected = correctedAll[['ra','dec']]
corrected['series'] = 'Corrected (Pointing)'
observed = field[field['target'] == True][['ra','dec']]

observed['series'] = 'Field.xml'
observed['ra'] = observed.apply(lambda x: -1*float(x['ra']) if float(x['ra']) < 0 else float(x['ra']), axis = 1)
observed.ra.astype(float)
observed.dec.astype(float)


sboffset = getSBOffsets(sbUID)
sb = getSBSummary(asdm.asdmDict['SBSummary'])
sbUID = sb.values[0][0]


target = getSBTargets(sbUID)
science = getSBScience(sbUID)
partId =  target[target['ObsParameter'] == science.entityPartId.values[0]].FieldSource.values[0]

predicted = sboffset[sboffset['partId'] == partId][['latitude','longitude']]
longitude, lat = sbfield[sbfield['entityPartId'] == partId][['longitude','latitude']].values[0]
predicted[['raoff','decoff']] = predicted[['longitude','latitude']].astype(float)
RA0 = float(longitude)*pl.pi/180.
Dec0 = float(lat)*pl.pi/180.

predicted['dRA'] = predicted.apply(lambda x: pl.radians(x['raoff']/3600.), axis = 1)
predicted['dDec'] = predicted.apply(lambda x: pl.radians(x['decoff']/3600.), axis = 1)
predicted['Pl'] = predicted.apply(lambda x: list((pl.cos(x['dRA'])*pl.cos(x['dDec']), pl.sin(x['dRA'])*pl.cos(x['dDec']), pl.sin(x['dDec']))) , axis = 1)
predicted['Ps'] = predicted.apply(lambda x: rot(x['Pl'],RA0,Dec0), axis = 1)
predicted['otcoor'] = predicted.apply(lambda x: list((pl.arctan2(x['Ps'][1], x['Ps'][0]) % (2.*pl.pi), pl.arcsin(x['Ps'][2]))), axis =1)

predictedList = list()
predictedList.append((float(longitude)*np.pi/180.,float(lat)*np.pi/180. ))

for i in predicted.values:
    predictedList.append( ( (float(longitude)+float(i[1])/3600.)*np.pi/180. , (float(lat)+float(i[0])/3600.)*np.pi/180))

pred = pd.DataFrame(predictedList, columns = ['ra','dec'])
pred['series'] = 'SchedBlock'

final = pd.concat([corrected,observed,pred])
final[['ra','dec']] =  final[['ra','dec']].astype(float)
groups = final.groupby('series')

fig, ax = plt.subplots()
ax.margins(0.05)
for name, group in groups:
    ax.plot(group.ra, group.dec, marker='.', linestyle='', ms=12, label=name, alpha=0.7)

ax.legend()
plt.show()


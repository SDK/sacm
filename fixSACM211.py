__author__ = 'sagonzal'
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
import pylab as pl
pd.options.display.width = 300
from itertools import combinations
from astropy import units as u
from astropy.coordinates import SkyCoord
from math import atan2
J0 = ephem.julian_date(0)


def azelToRaDec(az=None, el=None,lat=None,lon=None,alt=None, ut=None):
    global J0
    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lon)
    observer.elevation = alt
    observer.date = ut - J0
    return observer.radec_of(az, el)

def WriteNewField(fielduid = None, dir = None, df = None):
    fieldXML = GetXML(fielduid,'Field')
    if fieldXML is not False:
        f = minidom.parseString(fieldXML)
        r = f.getElementsByTagName('row')
        for i in r:
            fieldId = unicode(i.getElementsByTagName('fieldId')[0].firstChild.data)
            try:
                ra_new, dec_new = df[fieldId]
                text = ' 2 1 2 %s %s '%(ra_new,dec_new)
                i.getElementsByTagName('delayDir')[0].firstChild.replaceWholeText(text)
                i.getElementsByTagName('phaseDir')[0].firstChild.replaceWholeText(text)
                i.getElementsByTagName('referenceDir')[0].firstChild.replaceWholeText(text)
            except KeyError as e:
                pass

        open(dir+"Field.xml.new","wb").write(f.toxml())

def measureDistance(lat1, lon1, lat2, lon2):
    R = 6383.137 # Radius of earth at Chajnantor aprox. in KM
    dLat = (lat2 - lat1) * np.pi / 180.
    dLon = (lon2 - lon1) * np.pi / 180.
    a = pl.sin(dLat/2.) * pl.sin(dLat/2.) + pl.cos(lat1 * np.pi / 180.) * pl.cos(lat2 * np.pi / 180.) * pl.sin(dLon/2.) * pl.sin(dLon/2.)
    c = 2. * atan2(pl.sqrt(a), pl.sqrt(1-a))
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
main = getMain(asdm.asdmDict['Main'])


rows = asdmtable.pointingTable().get()
pointingList = list()
for idx,row in enumerate(rows):
    pointingList.append((idx, str(row.antennaId()), float(row.numSample()), float(row.numTerm()),str(row.timeInterval()), str(row.timeOrigin())))

pointingAll = pd.DataFrame(pointingList,columns = ['rowNum','antennaId','samples','iter','duration','origin'])

#TODO: Fix to match any antenna
pointing = pointingAll[pointingAll['antennaId'] == 'Antenna_1']

#do some transformations for matching the data
scan['target'] = scan.apply(lambda x: True if str(x['scanIntent']).find('OBSERVE_TARGET') > 0 else False ,axis = 1)
tsysScans = list(set(scan.sourceName[scan['target'] == True].values))
scan['target'] = scan.apply(lambda x: True if str(x['sourceName']) in tsysScans else x['target'] ,axis = 1)
targets = map(unicode.strip,list(scan[scan['target'] == True].sourceName.values))

source['target'] = source.apply(lambda x: True if str(x['sourceName']).strip() in targets else False, axis = 1)
source['ra'], source['dec'] = zip(*source.apply(lambda x: arrayParser(x['direction'],1), axis = 1))
field['target'] = field.apply(lambda x: True if str(x['fieldName']).strip() in targets else False, axis = 1)

foo = list(scan.scanNumber[scan['target'] == True])
bar = list(main.loc[main['scanNumber'].isin(foo) ]['fieldId'].unique())

pointing['go'] = False

#horrible hack to match the pointing table timescale with the subscan table
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
    dRA,dDec = [[float(str(p[0]).replace('rad','').replace(',','.')),float(str(p[1]).replace('rad','').replace(',','.'))] for p in row.sourceOffset() ][row.numSample()/2]
    Pl = [pl.cos(dRA)*pl.cos(dDec), pl.sin(dRA)*pl.cos(dDec), pl.sin(dDec)]
    Ps = rot(Pl, ra, dec)
    correctedList.append((pl.arctan2(Ps[1], Ps[0]) % (2.*pl.pi),  pl.arcsin(Ps[2]), i))

correctedAll = pd.DataFrame(correctedList, columns=['ra','dec', 'row'])
corrected = correctedAll[['ra','dec']]
corrected['series'] = 'Corrected (Pointing)'

observed = field[field['target'] == True][['fieldId','ra','dec']]
observed.ra = observed.ra.astype(float)
observed.dec = observed.dec.astype(float)
observed = observed.loc[observed['fieldId'].isin(bar) ]
observed = observed.reset_index(drop=True)
corrected = corrected.drop_duplicates()
corrected = corrected.reset_index(drop=True)
cat = SkyCoord(observed.ra.values * u.rad, observed.dec.values * u.rad, frame='icrs')
cat2 = SkyCoord(corrected.ra.values * u.rad, corrected.dec.values *u.rad, frame='icrs')
match, separ, dist = cat2.match_to_catalog_sky(cat)

observed['fieldId']

observed['series'] = 'Field.xml'
observed['ra'] = observed.apply(lambda x: -1*float(x['ra']) if float(x['ra']) < 0 else float(x['ra']), axis = 1)


#SB Queries and data manipulation
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
predicted['otcoor_ra'] = predicted.apply(lambda x: x['otcoor'][0], axis  =1 )
predicted['otcoor_dec'] = predicted.apply(lambda x: x['otcoor'][1], axis  =1 )
predictedList = list()
#predictedList.append((RA0,Dec0))
pred = pd.DataFrame(predictedList, columns = ['ra','dec'])
ot = predicted[['otcoor_ra','otcoor_dec']]
ot.columns= ['ra','dec']
pred = pd.concat([pred,ot])
pred['series'] = 'SchedBlock'

comb = combinations(geo[['lat','lon']].values, 2)
combList = list()
for i in comb:
    combList.append((i[0][0],i[0][1],i[1][0],i[1][1]))
baseLines = pd.DataFrame(combList)
baseLines['dist'] = baseLines.apply(lambda x: measureDistance(x[0],x[1],x[2],x[3]) , axis = 1)

blMax = baseLines.dist.describe().values[7]
sbfreq = np.float(sb.frequency.values[0])*1e9
c = 299792458
l = c / sbfreq
beam = l / blMax
sbeam = beam * 206264.80624709636


diff = pd.concat([observed.ix[match].reset_index(drop=True),corrected] , axis = 1)
diff.columns = ['fieldId','ra_field','dec_field','field','ra_pointing','dec_pointing','pointing']
diff['ra_diff'] = diff.apply(lambda x: pl.absolute(x['ra_field'] - x['ra_pointing'])*pl.cos(dec), axis = 1)
diff['dec_diff'] = diff.apply(lambda x: pl.absolute(x['dec_field'] - x['dec_pointing']), axis = 1)

diff['total'] = diff.apply(lambda x: ((x['ra_diff']**2 + x['dec_diff']**2)**(0.5))*206264.80624709636, axis = 1)

if diff.total.describe().values[7] >= sbeam /5.:
    print 'Needs New Field Table'
    print 'Mean Offset (arcsec) :',str(diff.total.describe().values[1])
    print 'Max Offset (arcsec) :',str(diff.total.describe().values[7])
    print 'Sbeam / 5:', str(sbeam /5.)
else:
    print 'Does not need fix'
    print 'Mean Offset (arcsec) :',str(diff.total.describe().values[1])
    print 'Max Offset (arcsec) :',str(diff.total.describe().values[7])
    print 'Sbeam / 5:', str(sbeam /5.)

#Plotting

new = diff[['fieldId','ra_pointing','dec_pointing']]
newDict = new.set_index('fieldId').T.to_dict('list')

WriteNewField(asdm.asdmDict['Field'] ,asdmdir ,newDict)

final = pd.concat([corrected,observed,pred])
final[['ra','dec']] =  final[['ra','dec']].astype(float)
groups = final.groupby('series')

fig, ax = plt.subplots()
ax.margins(0.05)
marks = ['.','+','x']
colors = ['b','r','k']

for idx, x in enumerate(groups):
    ax.plot(x[1].ra, x[1].dec, marker=marks[idx], color=colors[idx],linestyle='', ms=12, label=x[0], alpha=0.6)

ax.legend()
plt.show()


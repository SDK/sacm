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
asdmdir= 'uid___A002_X72c4aa_X614'
asdmtable.setFromFile(asdmdir, parser)
uid = asdmtable.entity().toString().split('"')[1]
asdm = AsdmCheck()
asdm.setUID(uid)

scan = getScan(asdm.asdmDict['Scan'])
subscan = getSubScan(asdm.asdmDict['Subscan'])
scan['target'] = scan.apply(lambda x: True if str(x['scanIntent']).find('OBSERVE_TARGET') > 0 else False ,axis = 1)
foo = list(scan.scanNumber[scan['target'] == True])
mosaic = subscan.loc[subscan['scanNumber'].isin(foo) ]

rows = asdmtable.pointingTable().get()
pointingList = list()

antenna = getAntennas(asdm.asdmDict['Antenna'])
station = getStation(asdm.asdmDict['Station'])
geo = pd.merge(antenna,station, left_on='stationId', right_on = 'stationId', how = 'inner')
geo['lat'], geo['lon'], geo['alt'] = zip(*geo.apply(lambda x: gh.turn_xyz_into_llh(float(x.pos[0]),float(x.pos[1]),float(x.pos[2]), 'wgs84'),axis=1))

for idx,row in enumerate(rows):
    pointingList.append((idx, str(row.antennaId()), float(row.numSample()), float(row.numTerm()),str(row.timeInterval()), str(row.timeOrigin())))
pointing = pd.DataFrame(pointingList,columns = ['rowNum','antennaId','samples','iter','duration','origin'])






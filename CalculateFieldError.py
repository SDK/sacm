__author__ = 'sagonzal'
from MetaData import *
import math
import sacm.geo_helper as gh
import pylab as pl
from itertools import combinations
import pandas as pd
import sys
def measureDistance(lat1, lon1, lat2, lon2):
    R = 6383.137 # Radius of earth at Chajnantor aprox. in KM
    dLat = (lat2 - lat1) * np.pi / 180.
    dLon = (lon2 - lon1) * np.pi / 180.
    a = pl.sin(dLat/2.) * pl.sin(dLat/2.) + pl.cos(lat1 * np.pi / 180.) * pl.cos(lat2 * np.pi / 180.) * pl.sin(dLon/2.) * pl.sin(dLon/2.)
    c = 2. * math.atan2(pl.sqrt(a), pl.sqrt(1-a))
    d = R * c
    return d * 1000. # meters

def rot(Pl, rLong, rLat):
    return [math.cos(rLong)*math.cos(rLat) * Pl[0] - math.sin(rLong) * Pl[1] - math.cos(rLong)*math.sin(rLat) * Pl[2],
           math.sin(rLong)*math.cos(rLat) * Pl[0] + math.cos(rLong) * Pl[1] - math.sin(rLong)*math.sin(rLat) * Pl[2],
           math.sin(rLat) * Pl[0] + math.cos(rLat) * Pl[2]]

def posByRotation(refRA, refDE, xi, eta):
    Pl = [math.cos(xi)*math.cos(eta), math.sin(xi)*math.cos(eta), math.sin(eta)]
    Ps = rot(Pl, refRA, refDE)
    return (math.atan2(Ps[1], Ps[0]) % (2.*math.pi), math.asin(Ps[2]))

def posErr(refRA, refDE, fieldRA, fieldDE):
    cosRefDE = math.cos(refDE)
    sinRefDE = math.sin(refDE)
    # get the intended offset, assuming simplistic formula was used
    xi = cosRefDE * (fieldRA - refRA)
    eta = fieldDE - refDE
    (offRA, offDE) = posByRotation(refRA, refDE, xi, eta)
    errHoriz = (offRA-refRA)*cosRefDE - xi
    errDE = (offDE-refDE) - eta
    errTot = math.sqrt(errHoriz*errHoriz + errDE*errDE)
    #print "xi, eta:               (%15.11f, %15.11f) = (%9.3f, %9.3f) arcsec" % (xi, eta, 3600.0*math.degrees(xi), 3600.0*math.degrees(eta))
    #print "reference       RA,DE: (%15.11f, %15.11f)" % (refRA, refDE)
    #print "offset 'rotate' RA,DE: (%15.11f, %15.11f)" % (offRA, offDE)
    #print "offset 'simple' RA,DE: (%15.11f, %15.11f)" % (refRA + xi/cosRefDE, refDE + eta)
    #print "err    Horiz, DE, total: %.2f, %.2f, %.2f milli-arcsec" % (3.6e6*math.degrees(errHoriz), 3.6e6*math.degrees(errDE), 3.6e6*math.degrees(errTot))
    return 3.6e6*math.degrees(errTot)

df = pd.read_csv('final.csv', sep='|', header=None)
asdm = AsdmCheck()
for row in df.values:
    uid = row[0]
    sb = row[1]
    project = row[2]
    asdm.setUID(uid)
    ################################################################
    #Calculate the 10% of the Resolution
    antenna = getAntennas(asdm.asdmDict['Antenna'])
    station = getStation(asdm.asdmDict['Station'])
    geo = pd.merge(antenna,station, left_on='stationId', right_on = 'stationId', how = 'inner')
    geo['pos'] = geo.apply(lambda x: arrayParser(x['position'],1) , axis = 1 )
    geo['lat'], geo['lon'], geo['alt'] = zip(*geo.apply(lambda x: gh.turn_xyz_into_llh(float(x.pos[0]),float(x.pos[1]),float(x.pos[2]), 'wgs84'),axis=1))
    comb = combinations(geo[['lat','lon']].values, 2)
    combList = list()
    for i in comb:
        combList.append((i[0][0],i[0][1],i[1][0],i[1][1]))
    baseLines = pd.DataFrame(combList)
    baseLines['dist'] = baseLines.apply(lambda x: measureDistance(x[0],x[1],x[2],x[3]) , axis = 1)
    blMax = baseLines.dist.describe().values[7]
    sbsummary = getSBSummary(asdm.asdmDict['SBSummary'])
    restfreq = float(sbsummary.values[0][3])*1e9
    c = 299792458
    l = c / restfreq
    beam = l / blMax
    sbeam = beam * 206264.80624709636 / 10.
    ##############################################################
    #Calculate all the Offsets errors
    field = getField(asdm.asdmDict['Field'])
    source = getSource(asdm.asdmDict['Source'])
    scan = getScan(asdm.asdmDict['Scan'])

    scan['target'] = scan.apply(lambda x: True if str(x['scanIntent']).find('OBSERVE_TARGET') > 0 else False ,axis = 1)
    targets = map(unicode.strip,list(scan[scan['target'] == True].sourceName.values))
    field['target'] = field.apply(lambda x: True if str(x['fieldName']).strip() in targets else False, axis = 1)
    source['target'] = source.apply(lambda x: True if str(x['sourceName']).strip() in targets else False, axis = 1)
    source['ra'], source['dec'] = zip(*source.apply(lambda x: arrayParser(x['direction'],1), axis = 1))
    del source['spectralWindowId']
    source = source.drop_duplicates()
    source2 = source[source['target'] == True]
    field['ra'],field['dec'] = zip(*field.apply(lambda x: arrayParser(x['referenceDir'],2)[0], axis = 1))
    field2 = field[field['target'] == True]
    diff = pd.merge(field2, source2, left_on='sourceId',right_on='sourceId',how='inner')
    diff['total'] = diff.apply(lambda x: posErr(float(x['ra_y']),float(x['dec_y']),float(x['ra_x']),float(x['dec_x'])), axis = 1)
    maxOffset = diff.total.describe()[7]/1000.
    #Check if the SB needs Re-Image
    print '|',uid,'|',sb,'|',project,'|',str(maxOffset),'|',sbeam,'|'





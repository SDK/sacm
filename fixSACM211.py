#!/bin/env python
from MetaData import *
import ASDM
from asdmTypes import *
from ASDM import *
from Pointing import *
from ASDMParseOptions import *
import sys
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

def getNewSource(f=None):
    sourceXML = open(f,'r')
    if sourceXML is not False:
        source = minidom.parseString(sourceXML.read())
        sourceList = list()
        rows = source.getElementsByTagName('row')
        #there are missing fields in some rows for the Source table.
        for i in rows:
            sourceList.append((int(i.getElementsByTagName('sourceId')[0].firstChild.data),
                               i.getElementsByTagName('timeInterval')[0].firstChild.data,
                               i.getElementsByTagName('direction')[0].firstChild.data,
                               i.getElementsByTagName('directionCode')[0].firstChild.data,
                               i.getElementsByTagName('sourceName')[0].firstChild.data,
                               i.getElementsByTagName('spectralWindowId')[0].firstChild.data))
        sourceXML.close()
        return pd.DataFrame(sourceList,columns=['sourceId','timeInterval','direction','directionCode','sourceName',
                                                'spectralWindowId'])
    else:
        return False

def getNewField(f=None):
    fieldXML = open(f,'r')
    if fieldXML is not False:
        f = minidom.parseString(fieldXML.read())
        fieldList = list()
        rows = f.getElementsByTagName('row')
        for i in rows:
            fieldList.append((i.getElementsByTagName('fieldId')[0].firstChild.data,
                              i.getElementsByTagName('fieldName')[0].firstChild.data,
                              i.getElementsByTagName('numPoly')[0].firstChild.data,
                              #i.getElementsByTagName('delayDir')[0].firstChild.data,
                              #i.getElementsByTagName('phaseDir')[0].firstChild.data,
                              i.getElementsByTagName('referenceDir')[0].firstChild.data,
                              int(i.getElementsByTagName('time')[0].firstChild.data),
                              i.getElementsByTagName('code')[0].firstChild.data,
                              i.getElementsByTagName('directionCode')[0].firstChild.data,
                              int(i.getElementsByTagName('sourceId')[0].firstChild.data)))
        #return pd.DataFrame(fieldList, columns=['fieldId', 'fieldName', 'numPoly','delayDir','phaseDir','referenceDir', 'time', 'code', 'directionCode', 'sourceId'])
        fieldXML.close()
        return pd.DataFrame(fieldList, columns=['fieldId', 'fieldName', 'numPoly','referenceDir', 'time', 'code', 'directionCode', 'sourceId'])
    else:
        return False

def WriteNewSource(sourceuid = None, dir = None, df = None):
    sourceXML = GetXML(sourceuid,'Source')
    if sourceXML is not False:
        f = minidom.parseString(sourceXML)
        r = f.getElementsByTagName('row')
        for i in r:
            sourceName = unicode(i.getElementsByTagName('sourceName')[0].firstChild.data).strip()
            direction = unicode(i.getElementsByTagName('direction')[0].firstChild.data).strip()
            try:
                text = str(df[(sourceName,direction)])
                i.getElementsByTagName('sourceId')[0].firstChild.replaceWholeText(text)
            except KeyError as e:
                pass
        open(dir+"/Source.xml.new","wb").write(f.toxml())

def WriteNewField(fielduid = None, dir = None, fieldDict = None, sourceDict=None):
    fieldXML = GetXML(fielduid,'Field')
    if fieldXML is not False:
        f = minidom.parseString(fieldXML)
        r = f.getElementsByTagName('row')
        for i in r:
            fieldId = unicode(i.getElementsByTagName('fieldId')[0].firstChild.data)
            sourceName = unicode(i.getElementsByTagName('fieldName')[0].firstChild.data).strip()
            referenceDir = unicode(i.getElementsByTagName('referenceDir')[0].firstChild.data).strip()
            try:
                sourceId = str(sourceDict[(sourceName,referenceDir[2:])])
            except KeyError as e:
                newDict = dict()
                for key, value in sourceDict.iteritems():
                    newDict[key[0]] = value
                sourceId = str(newDict[sourceName])
            i.getElementsByTagName('sourceId')[0].firstChild.replaceWholeText(sourceId)
            try:
                ra_new, dec_new = fieldDict[fieldId]
                text = ' 2 1 2 %.16f %.16f '%(ra_new,dec_new)
                i.getElementsByTagName('delayDir')[0].firstChild.replaceWholeText(text)
                i.getElementsByTagName('phaseDir')[0].firstChild.replaceWholeText(text)
                i.getElementsByTagName('referenceDir')[0].firstChild.replaceWholeText(text)
            except KeyError as e:
                pass

        open(dir+"/Field.xml.new","wb").write(f.toxml())

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
if len(sys.argv[1]) >= 1:
    asdmdir = sys.argv[1]
else:
    asdmdir = 'uid___A002_X826a79_Xcdb'

try:
    if sys.argv[2] == 'silent':
        silent = True
    else:
        silent = False
except IndexError as e:
    silent = False
    pass

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
subscan['target'] = subscan.apply(lambda x: True if str(x['fieldName']).strip() in targets else False, axis = 1)
source['ra'], source['dec'] = zip(*source.apply(lambda x: arrayParser(x['direction'],1), axis = 1))
field['target'] = field.apply(lambda x: True if str(x['fieldName']).strip() in targets else False, axis = 1)

list_of_targets = source[source['target'] ==True][['sourceName','ra','dec']].drop_duplicates()
g = pd.merge(subscan,list_of_targets, left_on = 'fieldName', right_on= 'sourceName', how = 'inner')
pointing['go'] = False
field['ra'],field['dec'] = zip(*field.apply(lambda x: arrayParser(x['referenceDir'],2)[0], axis = 1))
field['ra'] = field['ra'].astype(float)
field['dec'] = field['dec'].astype(float)
field['ra']  = field.apply(lambda x: 2*pl.pi + x['ra'] if x['ra'] < 0 else x['ra'], axis = 1)
correctedList = list()
fullbar = list()
for name, groups in g.groupby('sourceName'):
    foo = list(groups.scanNumber[groups['target'] == True])
    print foo
    bar = list(main.loc[main['scanNumber'].isin(foo) ]['fieldId'].unique())
    for i in bar:
        fullbar.append(i)
    for i in subscan.loc[subscan['scanNumber'].isin(foo) ][['startTime','endTime']].values:
            pointing['go'] = pointing.apply(lambda x: name if  prs.parse(sdmTimeString(i[0])) - datetime.timedelta(seconds=1) <= prs.parse(x['origin']) and prs.parse(sdmTimeString(i[1])) >= prs.parse(x['origin']) else x['go'], axis = 1)

    ra = float(groups[groups['target'] ==True]['ra'].unique()[0])
    if ra < 0:
        ra = ra * -1.
    dec = float(groups[groups['target'] ==True]['dec'].unique()[0])

    correctedList.append((ra,dec,0))
    for i in pointing.query('go == "%s"'%name).rowNum.values:
        row  = rows[i]
        dRA,dDec = [[p[0].get(),p[1].get()] for p in row.sourceOffset() ][row.numSample()/2]
    #    if dRA == 0. or dDec == 0.:
    #        print "no Offset positions in the Pointing Table"
    #        print "Is this EB a MultiSource?"
    #        sys.exit(1)
        Pl = [pl.cos(dRA)*pl.cos(dDec), pl.sin(dRA)*pl.cos(dDec), pl.sin(dDec)]
        Ps = rot(Pl, ra, dec)
        correctedList.append((pl.arctan2(Ps[1], Ps[0]) % (2.*pl.pi),  pl.arcsin(Ps[2]), i))

correctedAll = pd.DataFrame(correctedList, columns=['ra','dec', 'row'])
corrected = correctedAll[['ra','dec']]
corrected['series'] = 'Corrected (Pointing.bin)'
corrected = corrected.drop_duplicates()
corrected = corrected.reset_index(drop=True)

observed = field[field['target'] == True][['fieldId','ra','dec']]
observed.ra = observed.ra.astype(float)
observed.dec = observed.dec.astype(float)
observed['ra'] = observed.apply(lambda x: x['ra']*-1. if x['ra'] < 0.0 else x['ra'], axis = 1)
observed = observed.loc[observed['fieldId'].isin(fullbar) ]
observed = observed.reset_index(drop=True)
observed['series'] = 'Field.xml'


cat = SkyCoord(observed.ra.values * u.rad, observed.dec.values * u.rad, frame='icrs')
cat2 = SkyCoord(corrected.ra.values * u.rad, corrected.dec.values *u.rad, frame='icrs')
match, separ, dist = cat2.match_to_catalog_sky(cat)

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


print "###########################"
print "###### FIX SACM 211 #######"
print "###########################"
print "Number of pointings in Fields.xml: " , str(observed.ra.describe().values[0])
print "Number of pointings in Pointing  : " , str(corrected.ra.describe().values[0])
print 'Mean Offset (arcsec) :',str(diff.total.describe().values[1])
print 'Max Offset (arcsec) :',str(diff.total.describe().values[7])
print '10% Sbeam :', str(sbeam /10.)
print "###########################"
print "The Fields are matching the following Sources"
print source[source['sourceId'].isin(field.query('target == True').sourceId.unique())][['sourceId','sourceName']].drop_duplicates()
print "###########################"
print source[['sourceId','sourceName','ra','dec']].drop_duplicates()
print "###########################"
print field


#Field == Pointing, no fix in Main.xml
#Field > Pointing, fix in Main.xml, replace the old fieldIds with new ones
#Field < Pointing , re index new pointings and add them into the list of fields <<< Should NOT HAPPEND!

    #Normal Fix
if not silent:
    doit = raw_input('\n Would you like to rebuild Source Table? (Y/n)')
    if 'Y' in doit or 'y' in doit or len(doit)==0:
        df = source[['sourceName','direction']].drop_duplicates().reset_index(drop=True)
        df['sourceName'] = df.apply(lambda x: unicode(x['sourceName']).strip(), axis = 1)
        df['direction'] = df.apply(lambda x: unicode(x['direction']).strip(), axis = 1)
        sourceDict = dict(zip(zip(df.sourceName.values, df.direction.values),df.index))
        WriteNewSource(asdm.asdmDict['Source'],asdmdir,sourceDict)
        newSource = getNewSource(asdmdir+'/Source.xml.new')
        print "New Values for Source table"
        print newSource[['sourceId','sourceName','direction']].drop_duplicates()
        new = diff[['fieldId','ra_pointing','dec_pointing']]
        newDict = new.set_index('fieldId').T.to_dict('list')
        WriteNewField(asdm.asdmDict['Field'] ,asdmdir ,fieldDict=newDict, sourceDict=sourceDict)
        print "New Values for Fields Table"
        newField = getNewField(asdmdir+'/Field.xml.new')
        print newField
    else:
        df = source[['sourceName','direction']].drop_duplicates().reset_index(drop=True)
        df['sourceName'] = df.apply(lambda x: unicode(x['sourceName']).strip(), axis = 1)
        df['direction'] = df.apply(lambda x: unicode(x['direction']).strip(), axis = 1)
        sourceDict = dict(zip(zip(df.sourceName.values, df.direction.values),df.index))
        new = diff[['fieldId','ra_pointing','dec_pointing']]
        newDict = new.set_index('fieldId').T.to_dict('list')
        WriteNewField(asdm.asdmDict['Field'] ,asdmdir ,fieldDict=newDict, sourceDict=sourceDict)
        print "New Values for Fields Table"
        newField = getNewField(asdmdir+'/Field.xml.new')
        print newField
else:
    df = source[['sourceName','direction']].drop_duplicates().reset_index(drop=True)
    df['sourceName'] = df.apply(lambda x: unicode(x['sourceName']).strip(), axis = 1)
    df['direction'] = df.apply(lambda x: unicode(x['direction']).strip(), axis = 1)
    sourceDict = dict(zip(zip(df.sourceName.values, df.direction.values),df.index))
    WriteNewSource(asdm.asdmDict['Source'],asdmdir,sourceDict)
    newSource = getNewSource(asdmdir+'/Source.xml.new')
    print "New Values for Source table"
    print newSource[['sourceId','sourceName','direction']].drop_duplicates()
    new = diff[['fieldId','ra_pointing','dec_pointing']]
    newDict = new.set_index('fieldId').T.to_dict('list')
    WriteNewField(asdm.asdmDict['Field'] ,asdmdir ,fieldDict=newDict, sourceDict=sourceDict)
    print "New Values for Fields Table"
    newField = getNewField(asdmdir+'/Field.xml.new')
    print newField




final = pd.concat([corrected,observed])
final[['ra','dec']] =  final[['ra','dec']].astype(float)
groups = final.groupby('series')

if silent:
    fig, ax = plt.subplots()
    ax.margins(0.05)
    marks = ['.','+','x']
    colors = ['b','r','k']
    for idx, x in enumerate(groups):
        ax.plot(x[1].ra, x[1].dec, marker=marks[idx], color=colors[idx],linestyle='', ms=12, label=x[0], alpha=0.6)
    ax.legend()
    plt.savefig(asdmdir+'/'+asdmdir+'.png', bbox_inches='tight')
else:
    fig, ax = plt.subplots()
    ax.margins(0.05)
    marks = ['.','+','x']
    colors = ['b','r','k']
    for idx, x in enumerate(groups):
        ax.plot(x[1].ra, x[1].dec, marker=marks[idx], color=colors[idx],linestyle='', ms=12, label=x[0], alpha=0.6)
    ax.legend()
    plt.show()




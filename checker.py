# -*- coding: utf-8 -*-
__author__ = 'sdk'
from sacm import *
from xml.dom import minidom
import pandas as pd

asdmUID = ''


def getASDM(uid=None):
    asdmXML = GetXML(uid,'ASDM')
    if asdmXML is not False:
        asdm = minidom.parseString(asdmXML)
        rows = asdm.getElementsByTagName('Table')
        asdmList = list()
        for i in rows:
            if int(i.getElementsByTagName('NumberRows')[0].firstChild.data) != 0:
                #print i.getElementsByTagName('Name')[0].firstChild.data,i.getElementsByTagName('NumberRows')[0].firstChild.data
                asdmList.append((i.getElementsByTagName('Name')[0].firstChild.data,
                                 i.getElementsByTagName('NumberRows')[0].firstChild.data,
                                 str(i.getElementsByTagName('Entity')[0].getAttribute('entityTypeName')),
                                 str(i.getElementsByTagName('Entity')[0].getAttribute('entityId'))))
        toc = asdm.getElementsByTagName('TimeOfCreation')[0].firstChild.data

        return asdmList, pd.DataFrame(asdmList, columns=['table', 'numrows', 'typename', 'uid'],) , datetime.datetime.strptime(toc.strip()[0:19],"%Y-%m-%dT%H:%M:%S" )

    else:
        return False




def getMain(uid=None):
    mainXML = GetXML(uid,'Main')
    if mainXML is not False:
        main = minidom.parseString(mainXML)
        mainList = list()
        rows = main.getElementsByTagName('row')
        for i in rows:
            #print i.getElementsByTagName('time')[0].firstChild.data, i.getElementsByTagName('stateId')[0].firstChild.data
            mainList.append((sdmTimeString(int(i.getElementsByTagName('time')[0].firstChild.data)),
                             #i.getElementsByTagName('numAntenna')[0].firstChild.data,
                             i.getElementsByTagName('timeSampling')[0].firstChild.data,
                             int(i.getElementsByTagName('interval')[0].firstChild.data),
                             #i.getElementsByTagName('numIntegration')[0].firstChild.data,
                             int(i.getElementsByTagName('scanNumber')[0].firstChild.data),
                             int(i.getElementsByTagName('subscanNumber')[0].firstChild.data),
                             int(i.getElementsByTagName('dataSize')[0].firstChild.data),
                             i.getElementsByTagName('dataUID')[0].getElementsByTagName('EntityRef')[0].getAttribute('entityId'),
                             i.getElementsByTagName('fieldId')[0].firstChild.data,
                             i.getElementsByTagName('stateId')[0].firstChild.data))
        return pd.DataFrame(mainList, columns=['time', 'timeSampling', 'interval', 'scanNumber',
                                             'subscanNumber', 'dataSize', 'dataUID', 'fieldId', 'stateId'])
    else:
        return False

def getAntennas(uid=None):
    antennaXML = GetXML(uid,'Antenna')
    if antennaXML is not False:
        antenna = minidom.parseString(antennaXML)
        antennaList = list()
        rows = antenna.getElementsByTagName('row')
        for i in rows:
            antennaList.append((
                i.getElementsByTagName('antennaId')[0].firstChild.data,
                i.getElementsByTagName('name')[0].firstChild.data,
                i.getElementsByTagName('antennaMake')[0].firstChild.data,
                i.getElementsByTagName('dishDiameter')[0].firstChild.data,
                i.getElementsByTagName('stationId')[0].firstChild.data,
            ))
        return pd.DataFrame(antennaList,columns=['antennaId','name','antennaMake','dishDiameter','stationId'])
    else:
        return False

def getSBSummary(uid=None):
    summaryXML = GetXML(uid,'SBSummary')
    if summaryXML is not False:
        summary = minidom.parseString(summaryXML)
        summaryList = list()
        rows = summary.getElementsByTagName('row')
        for i in rows:
            summaryList.append((i.getElementsByTagName('sbSummaryUID')[0].getElementsByTagName('EntityRef')[0].getAttribute('entityId'),
                                i.getElementsByTagName('projectUID')[0].getElementsByTagName('EntityRef')[0].getAttribute('entityId'),
                                i.getElementsByTagName('obsUnitSetUID')[0].getElementsByTagName('EntityRef')[0].getAttribute('entityId'),
                             float(i.getElementsByTagName('frequency')[0].firstChild.data),
                             i.getElementsByTagName('frequencyBand')[0].firstChild.data,
                             i.getElementsByTagName('scienceGoal')[0].firstChild.data,
                             i.getElementsByTagName('weatherConstraint')[0].firstChild.data ))

        return pd.DataFrame(summaryList, columns=['sbSummaryUID', 'projectUID', 'obsUnitSetUID', 'frequency',
                                             'frequencyBand', 'scienceGoal', 'weatherConstraint'])
    else:
        return False

def getScan(uid=None):
    scanXML = GetXML(uid,'Scan')
    if scanXML is not False:
        scan = minidom.parseString(scanXML)
        scanList = list()
        rows = scan.getElementsByTagName('row')
        for i in rows:
            try:
                scanList.append((int(i.getElementsByTagName('scanNumber')[0].firstChild.data),
                                 int(i.getElementsByTagName('startTime')[0].firstChild.data),
                                 int(i.getElementsByTagName('endTime')[0].firstChild.data),
                                 #i.getElementsByTagName('numIntent')[0].firstChild.data,
                                 int(i.getElementsByTagName('numSubscan')[0].firstChild.data),
                                 arrayParser(i.getElementsByTagName('scanIntent')[0].firstChild.data, 1),
                                 arrayParser(i.getElementsByTagName('calDataType')[0].firstChild.data, 1),
                                 int(i.getElementsByTagName('numField')[0].firstChild.data),
                                 i.getElementsByTagName('fieldName')[0].firstChild.data,
                                 i.getElementsByTagName('sourceName')[0].firstChild.data))
            except IndexError as e:
                scanList.append((int(i.getElementsByTagName('scanNumber')[0].firstChild.data),
                                 int(i.getElementsByTagName('startTime')[0].firstChild.data),
                                 int(i.getElementsByTagName('endTime')[0].firstChild.data),
                                 #i.getElementsByTagName('numIntent')[0].firstChild.data,
                                 int(i.getElementsByTagName('numSubscan')[0].firstChild.data),
                                 arrayParser(i.getElementsByTagName('scanIntent')[0].firstChild.data, 1),
                                 arrayParser(i.getElementsByTagName('calDataType')[0].firstChild.data, 1),
                                 0,
                                 "None",
                                 "None"))


        return pd.DataFrame(scanList, columns=['scanNumber', 'startTime', 'endTime', 'numSubscan',
                                             'scanIntent', 'calDataType', 'numField', 'fieldName', 'sourceName'])
    else:
        return False

def getStation(uid=None):
    stationXML = GetXML(uid,'Station')
    if stationXML is not False:
        station = minidom.parseString(stationXML)
        stationList = list()
        rows = station.getElementsByTagName('row')
        for i in rows:
            try:
                stationList.append((
                    i.getElementsByTagName('stationId')[0].firstChild.data,
                    i.getElementsByTagName('name')[0].firstChild.data,
                    i.getElementsByTagName('position')[0].firstChild.data,
                    i.getElementsByTagName('type')[0].firstChild.data,
                ))
            except IndexError as error:
                print error
                return False
    return pd.DataFrame(stationList ,columns=['stationId','name','position','type'])



def getSubScan(uid=None):
    subscanXML = GetXML(uid,'Subscan')
    if subscanXML is not False:
        subscan = minidom.parseString(subscanXML)
        subscanList = list()
        rows = subscan.getElementsByTagName('row')
        for i in rows:
            subscanList.append((int(i.getElementsByTagName('scanNumber')[0].firstChild.data),
                                int(i.getElementsByTagName('subscanNumber')[0].firstChild.data),
                                int(i.getElementsByTagName('startTime')[0].firstChild.data),
                                int(i.getElementsByTagName('endTime')[0].firstChild.data),
                                i.getElementsByTagName('fieldName')[0].firstChild.data,
                                i.getElementsByTagName('subscanIntent')[0].firstChild.data,
                                i.getElementsByTagName('subscanMode')[0].firstChild.data,
                                #i.getElementsByTagName('numIntegration')[0].firstChild.data,
                                #i.getElementsByTagName('numSubintegration')[0].firstChild.data,
                                #i.getElementsByTagName('correlatorCalibration')[0].firstChild.data
                                ))
        return pd.DataFrame(subscanList, columns=['scanNumber','subscanNumber','startTime','endTime','fieldName',
                                                  'subscanIntent','subscanMode'])
    else:
        return False


def getSource(uid=None):
    sourceXML = GetXML(uid,'Source')
    if sourceXML is not False:
        source = minidom.parseString(sourceXML)
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
        return pd.DataFrame(sourceList,columns=['sourceId','timeInterval','direction','directionCode','sourceName',
                                                'spectralWindowId'])
    else:
        return False


def getSpectralWindow(uid=None):
    spwXML = GetXML(uid,'SpectralWindow')
    if spwXML is not False:
        spw = minidom.parseString(spwXML)
        spwList = list()
        rows = spw.getElementsByTagName('row')
        for i in rows:
            if int(i.getElementsByTagName('numChan')[0].firstChild.data) > 4:
                try:
                    spwList.append((i.getElementsByTagName('spectralWindowId')[0].firstChild.data,
                                    i.getElementsByTagName('basebandName')[0].firstChild.data,
                                    i.getElementsByTagName('netSideband')[0].firstChild.data,
                                    int(i.getElementsByTagName('numChan')[0].firstChild.data),
                                    float(i.getElementsByTagName('refFreq')[0].firstChild.data),
                                    i.getElementsByTagName('sidebandProcessingMode')[0].firstChild.data,
                                    float(i.getElementsByTagName('totBandwidth')[0].firstChild.data),
                                    i.getElementsByTagName('chanFreqStart')[0].firstChild.data,
                                    i.getElementsByTagName('chanFreqStep')[0].firstChild.data,
                                    i.getElementsByTagName('chanWidth')[0].firstChild.data,
                                    i.getElementsByTagName('effectiveBw')[0].firstChild.data,
                                    i.getElementsByTagName('name')[0].firstChild.data,
                                    #i.getElementsByTagName('resolutionArray')[0].firstChild.data,
                                    i.getElementsByTagName('assocNature')[0].firstChild.data,
                                    i.getElementsByTagName('assocSpectralWindowId')[0].firstChild.data))
                except IndexError as e:
                    print e

        return pd.DataFrame(spwList, columns=['spectralWindowId', 'basebandName', 'netSideband', 'numChan',
                                             'refFreq', 'sidebandProcessingMode', 'totBandwidth', 'chanFreqStart','chanFreqStep','chanWidth',
                                             'effectiveBw', 'name',
                                             'assocNature', 'assocSpectralWindowId'])
    else:
        return False


def getField(uid=None):
    fieldXML = GetXML(uid,'Field')
    if fieldXML is not False:
        field = minidom.parseString(fieldXML)
        fieldList = list()
        rows = field.getElementsByTagName('row')
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
        return pd.DataFrame(fieldList, columns=['fieldId', 'fieldName', 'numPoly','referenceDir', 'time', 'code', 'directionCode', 'sourceId'])
    else:
        return False

def getSysCal(uid=None):
    syscalXML = GetXML(uid,'SysCal')
    if syscalXML is not False:
        syscal = minidom.parseString(syscalXML)
        syscalList = list()
        rows = syscal.getElementsByTagName('row')
        for i in rows:
            syscalList.append((
                i.getElementsByTagName('timeInterval')[0].firstChild.data,
                i.getElementsByTagName('numReceptor')[0].firstChild.data,
                i.getElementsByTagName('numChan')[0].firstChild.data,
                i.getElementsByTagName('tcalFlag')[0].firstChild.data,
                i.getElementsByTagName('tcalSpectrum')[0].firstChild.data,
                i.getElementsByTagName('trxFlag')[0].firstChild.data,
                i.getElementsByTagName('trxSpectrum')[0].firstChild.data,
                i.getElementsByTagName('tskyFlag')[0].firstChild.data,
                i.getElementsByTagName('tskySpectrum')[0].firstChild.data,
                i.getElementsByTagName('tsysFlag')[0].firstChild.data,
                i.getElementsByTagName('tsysSpectrum')[0].firstChild.data,
                i.getElementsByTagName('antennaId')[0].firstChild.data.strip(),
                i.getElementsByTagName('feedId')[0].firstChild.data,
                i.getElementsByTagName('spectralWindowId')[0].firstChild.data.strip() ))
        return pd.DataFrame(syscalList, columns=['timeInterval','numReceptor','numChan','tcalFlag','tcalSpectrum','trxFlag',
                                                 'trxSpectrum','tskyFlag','tskySpectrum','tsysFlag','tsysSpectrum','antennaId',
                                                 'feedId','spectralWindowId'])
    else:
        return False


def getSBData(sbuid=None):
    schedXML = GetXML(sbuid, 'SchedBlock')
    sched = minidom.parseString(schedXML)

    schedList = list()
    rowsBL = sched.getElementsByTagName('sbl:BLSpectralWindow')
    rowsACA = sched.getElementsByTagName('sbl:ACASpectralWindow')
    rows = rowsBL if len(rowsBL) > len(rowsACA) else rowsACA
    for i in rows:
        brother = i.parentNode.getElementsByTagName('sbl:BaseBandSpecificationRef')
        parent = i.parentNode.parentNode.parentNode
        schedList.append((
            parent.getAttribute('entityPartId'),
            parent.getAttribute('switchingType'),
            #parent.getAttribute('receiverType'),
            parent.getElementsByTagName('sbl:name')[0].firstChild.data,
            brother[0].getAttribute('entityId'),
            brother[0].getAttribute('partId'),
            #brother[0].getAttribute('entityTypeName'),
            #i.getAttribute('sideBand'),
            #i.getAttribute('windowFunction'),
            i.getAttribute('polnProducts'),
            #i.getAttribute('correlationBits'),
            i.getElementsByTagName('sbl:centerFrequency')[0].firstChild.data,
            i.getElementsByTagName('sbl:centerFrequency')[0].getAttribute('unit'),
            #i.getElementsByTagName('sbl:spectralAveragingFactor')[0].firstChild.data,
            #i.getElementsByTagName('sbl:name')[0].firstChild.data,
            i.getElementsByTagName('sbl:effectiveBandwidth')[0].firstChild.data,
            i.getElementsByTagName('sbl:effectiveBandwidth')[0].getAttribute('unit'),
            i.getElementsByTagName('sbl:effectiveNumberOfChannels')[0].firstChild.data,
            #i.getElementsByTagName('sbl:useThisSpectralWindow')[0].firstChild.data,
            i.getElementsByTagName('sbl:ChannelAverageRegion')[0].getElementsByTagName('sbl:startChannel')[0].firstChild.data,
            i.getElementsByTagName('sbl:ChannelAverageRegion')[0].getElementsByTagName('sbl:numberChannels')[0].firstChild.data,

        ))

    specs = pd.DataFrame(schedList)

    rows = sched.getElementsByTagName('sbl:BaseBandSpecification')
    bbList = list()

    for i in rows:
        parent = i.parentNode
        bbList.append((
            parent.getAttribute('receiverBand'),
            parent.getAttribute('dopplerReference'),
            parent.getElementsByTagName('sbl:restFrequency')[0].firstChild.data,
            parent.getElementsByTagName('sbl:restFrequency')[0].getAttribute('unit'),
            parent.getElementsByTagName('sbl:frequencySwitching')[0].firstChild.data,
            parent.getElementsByTagName('sbl:lO2Frequency')[0].firstChild.data,
            parent.getElementsByTagName('sbl:lO2Frequency')[0].getAttribute('unit'),
            #parent.getElementsByTagName('sbl:weighting')[0].firstChild.data,
            #parent.getElementsByTagName('sbl:useUSB')[0].firstChild.data,
            #parent.getElementsByTagName('sbl:use12GHzFilter')[0].firstChild.data,
            #parent.getElementsByTagName('sbl:imageCenterFrequency')[0].firstChild.data,
            #parent.getElementsByTagName('sbl:imageCenterFrequency')[0].getAttribute('unit'),
            i.getAttribute('entityPartId'),
            i.getAttribute('baseBandName'),
            #i.getAttribute('sideBandPreference'),
            i.getElementsByTagName('sbl:centerFrequency')[0].firstChild.data,
            i.getElementsByTagName('sbl:lO2Frequency')[0].firstChild.data,
            i.getElementsByTagName('sbl:lO2Frequency')[0].getAttribute('unit'),
            #i.getElementsByTagName('sbl:weighting')[0].firstChild.data,
            #i.getElementsByTagName('sbl:useUSB')[0].firstChild.data,
            #i.getElementsByTagName('sbl:use12GHzFilter')[0].firstChild.data,
            #i.getElementsByTagName('sbl:imageCenterFrequency')[0].firstChild.data,
            #i.getElementsByTagName('sbl:imageCenterFrequency')[0].getAttribute('unit')
        ))

    bb = pd.DataFrame(bbList)
    targetList = list()
    rows = sched.getElementsByTagName('sbl:Target')
    for i in rows:
        targetList.append((
            i.getAttribute('entityPartId'),
            i.getElementsByTagName('sbl:AbstractInstrumentSpecRef')[0].getAttribute('partId'),
            i.getElementsByTagName('sbl:FieldSourceRef')[0].getAttribute('partId'),
            i.getElementsByTagName('sbl:ObservingParametersRef')[0].getAttribute('partId'),
        ))

    target = pd.DataFrame(targetList, columns=['entityPartId', 'InstrumentSpec', 'FieldSource', 'ObsParameter'])

    rows = sched.getElementsByTagName('sbl:ScienceParameters')
    scienceList = list()
    for i in rows:
        scienceList.append((
            i.getAttribute('entityPartId'),
            i.getElementsByTagName('sbl:name')[0].firstChild.data,
            i.getElementsByTagName('sbl:representativeBandwidth')[0].firstChild.data,
            i.getElementsByTagName('sbl:representativeBandwidth')[0].getAttribute('unit'),
            i.getElementsByTagName('sbl:representativeFrequency')[0].firstChild.data,
            i.getElementsByTagName('sbl:representativeFrequency')[0].getAttribute('unit'),
            i.getElementsByTagName('sbl:sensitivityGoal')[0].firstChild.data,
            i.getElementsByTagName('sbl:sensitivityGoal')[0].getAttribute('unit'),
            i.getElementsByTagName('sbl:integrationTime')[0].firstChild.data,
            i.getElementsByTagName('sbl:integrationTime')[0].getAttribute('unit'),
            i.getElementsByTagName('sbl:subScanDuration')[0].firstChild.data,
            i.getElementsByTagName('sbl:subScanDuration')[0].getAttribute('unit'),
            i.getElementsByTagName('sbl:forceAtmCal')[0].firstChild.data
        ))

    science = pd.DataFrame(scienceList)

    rows = sched.getElementsByTagName('sbl:PhaseCalParameters')
    phaseList = list()
    for i in rows:
        phaseList.append((
            i.getAttribute('entityPartId'),
            #i.getElementsByTagName('sbl:name')[0].firstChild.data,
            i.getElementsByTagName('sbl:cycleTime')[0].firstChild.data,
            i.getElementsByTagName('sbl:cycleTime')[0].getAttribute('unit'),
            i.getElementsByTagName('sbl:defaultIntegrationTime')[0].firstChild.data,
            i.getElementsByTagName('sbl:defaultIntegrationTime')[0].getAttribute('unit'),
            i.getElementsByTagName('sbl:subScanDuration')[0].firstChild.data,
            i.getElementsByTagName('sbl:subScanDuration')[0].getAttribute('unit'),
            i.getElementsByTagName('sbl:forceAtmCal')[0].firstChild.data,
            i.getElementsByTagName('sbl:forceExecution')[0].firstChild.data
        ))

    phase = pd.DataFrame(phaseList)

    rows = sched.getElementsByTagName('sbl:FieldSource')
    fieldList = list()
    for i in rows:
        fieldList.append((
            i.getAttribute('entityPartId'),
            i.getAttribute('solarSystemObject'),
            i.getElementsByTagName('sbl:sourceName')[0].firstChild.data,
            #i.getElementsByTagName('sbl:sourceEphemeris')[0].firstChild.data,
            i.getElementsByTagName('sbl:name')[0].firstChild.data,
        ))

    field = pd.DataFrame(fieldList)
    return bb,specs,target,phase,science,field

def getSBFields(sbuid=None):
    schedXML = GetXML(sbuid, 'SchedBlock')
    sched = minidom.parseString(schedXML)

    rows = sched.getElementsByTagName('sbl:FieldSource')
    fieldList = list()
    for i in rows:
        fieldList.append((
            i.getAttribute('entityPartId'),
            i.getAttribute('solarSystemObject'),
            i.getElementsByTagName('sbl:sourceName')[0].firstChild.data,
            #i.getElementsByTagName('sbl:sourceEphemeris')[0].firstChild.data,
            i.getElementsByTagName('sbl:name')[0].firstChild.data,
            i.getElementsByTagName('sbl:sourceCoordinates')[0].getElementsByTagName('val:longitude')[0].firstChild.data,
            i.getElementsByTagName('sbl:sourceCoordinates')[0].getElementsByTagName('val:latitude')[0].firstChild.data,

        ))

    field = pd.DataFrame(fieldList, columns=['entityPartId','solarSystemObject','sourceName','name','longitude','latitude'])
    return field

def getSBScience(sbuid=None):
    schedXML = GetXML(sbuid, 'SchedBlock')
    sched = minidom.parseString(schedXML)

    rows = sched.getElementsByTagName('sbl:ScienceParameters')
    scienceList = list()
    for i in rows:
        scienceList.append((
            i.getAttribute('entityPartId'),
            i.getElementsByTagName('sbl:name')[0].firstChild.data,
            i.getElementsByTagName('sbl:representativeBandwidth')[0].firstChild.data,
            i.getElementsByTagName('sbl:representativeBandwidth')[0].getAttribute('unit'),
            i.getElementsByTagName('sbl:representativeFrequency')[0].firstChild.data,
            i.getElementsByTagName('sbl:representativeFrequency')[0].getAttribute('unit'),
            i.getElementsByTagName('sbl:sensitivityGoal')[0].firstChild.data,
            i.getElementsByTagName('sbl:sensitivityGoal')[0].getAttribute('unit'),
            i.getElementsByTagName('sbl:integrationTime')[0].firstChild.data,
            i.getElementsByTagName('sbl:integrationTime')[0].getAttribute('unit'),
            i.getElementsByTagName('sbl:subScanDuration')[0].firstChild.data,
            i.getElementsByTagName('sbl:subScanDuration')[0].getAttribute('unit'),
            i.getElementsByTagName('sbl:forceAtmCal')[0].firstChild.data
        ))

    science = pd.DataFrame(scienceList, columns=['entityPartId','name','representativeBandwidth','unit_rb','representativeFrequency','unit_rf',
                                                 'sensitivityGoal','unit_sg','integrationTime','unit_it','subScanDuration','unit_sc','forceAtmCal'])
    return science

def getSBTargets(sbuid=None):
    schedXML = GetXML(sbuid, 'SchedBlock')
    sched = minidom.parseString(schedXML)
    targetList = list()
    rows = sched.getElementsByTagName('sbl:Target')
    for i in rows:
        targetList.append((
            i.getAttribute('entityPartId'),
            i.getElementsByTagName('sbl:AbstractInstrumentSpecRef')[0].getAttribute('partId'),
            i.getElementsByTagName('sbl:FieldSourceRef')[0].getAttribute('partId'),
            i.getElementsByTagName('sbl:ObservingParametersRef')[0].getAttribute('partId'),
        ))

    target = pd.DataFrame(targetList, columns=['entityPartId', 'InstrumentSpec', 'FieldSource', 'ObsParameter'])
    return target

def getSBOffsets(sbuid=None):
    schedXML = GetXML(sbuid, 'SchedBlock')
    sched = minidom.parseString(schedXML)
    offsetList = list()
    rows = sched.getElementsByTagName('sbl:phaseCenterCoordinates')
    for i in rows:
        offsetList.append((
            i.parentNode.parentNode.getAttribute('entityPartId'),
            i.getAttribute('system'),
            i.getAttribute('type'),
            i.getElementsByTagName('val:longitude')[0].firstChild.data,
            i.getElementsByTagName('val:longitude')[0].getAttribute('unit'),
            i.getElementsByTagName('val:latitude')[0].firstChild.data,
            i.getElementsByTagName('val:latitude')[0].getAttribute('unit'),
        ))

    offset = pd.DataFrame(offsetList, columns=['partId','system', 'type', 'longitude','lon_unit', 'latitude','lat_unit'])
    return offset

def getScienceGoal(prjUID=None):
    projXML = GetXML(prjUID, 'ObsProject')
    proj = minidom.parseString(projXML)
    scienceGoalList = list()
    rows = proj.getElementsByTagName('prj:ScienceSpectralWindow')

    for i in rows:
        scienceGoalList.append((
            i.parentNode.parentNode.getElementsByTagName('prj:name')[0].firstChild.data,
            i.parentNode.parentNode.getElementsByTagName('prj:ObsUnitSetRef')[0].getAttribute('entityId'),
            i.parentNode.parentNode.getElementsByTagName('prj:ObsUnitSetRef')[0].getAttribute('partId'),
            i.parentNode.getElementsByTagName('prj:representativeFrequency')[0].firstChild.data,
            i.parentNode.getElementsByTagName('prj:userRepresentativeFrequency')[0].firstChild.data,
            i.getElementsByTagName('prj:centerFrequency')[0].firstChild.data,
            i.getElementsByTagName('prj:representativeWindow')[0].firstChild.data,
        ))

    scienceGoal = pd.DataFrame(scienceGoalList)
    return scienceGoal



def getSB_spectralconf(sbuid=None):
    schedXML = GetXML(sbuid, 'SchedBlock')
    sched = minidom.parseString(schedXML)

    schedList = list()
    rowsBL = sched.getElementsByTagName('sbl:BLSpectralWindow')
    rowsACA = sched.getElementsByTagName('sbl:ACASpectralWindow')
    rows = rowsBL if len(rowsBL) > len(rowsACA) else rowsACA
    for i in rows:
        brother = i.parentNode.getElementsByTagName('sbl:BaseBandSpecificationRef')
        parent = i.parentNode.parentNode.parentNode
        schedList.append((
            parent.getAttribute('entityPartId'),
            parent.getAttribute('switchingType'),
            #parent.getAttribute('receiverType'),
            parent.getElementsByTagName('sbl:name')[0].firstChild.data,
            brother[0].getAttribute('entityId'),
            brother[0].getAttribute('partId'),
            #brother[0].getAttribute('entityTypeName'),
            #i.getAttribute('sideBand'),
            #i.getAttribute('windowFunction'),
            #i.getAttribute('polnProducts'),
            #i.getAttribute('correlationBits'),
            #i.getElementsByTagName('sbl:centerFrequency')[0].firstChild.data,
            #i.getElementsByTagName('sbl:centerFrequency')[0].getAttribute('unit'),
            #i.getElementsByTagName('sbl:spectralAveragingFactor')[0].firstChild.data,
            #i.getElementsByTagName('sbl:name')[0].firstChild.data,
            #i.getElementsByTagName('sbl:effectiveBandwidth')[0].firstChild.data,
            #i.getElementsByTagName('sbl:effectiveBandwidth')[0].getAttribute('unit'),
            #i.getElementsByTagName('sbl:effectiveNumberOfChannels')[0].firstChild.data,
            #i.getElementsByTagName('sbl:useThisSpectralWindow')[0].firstChild.data,
            #i.getElementsByTagName('sbl:ChannelAverageRegion')[0].getElementsByTagName('sbl:startChannel')[0].firstChild.data,
            #i.getElementsByTagName('sbl:ChannelAverageRegion')[0].getElementsByTagName('sbl:numberChannels')[0].firstChild.data,

        ))

    specs = pd.DataFrame(schedList)

    rows = sched.getElementsByTagName('sbl:BaseBandSpecification')
    bbList = list()

    for i in rows:
        parent = i.parentNode
        bbList.append((
            parent.getAttribute('receiverBand'),
            #parent.getAttribute('dopplerReference'),
            #parent.getElementsByTagName('sbl:restFrequency')[0].firstChild.data,
            #parent.getElementsByTagName('sbl:restFrequency')[0].getAttribute('unit'),
            #parent.getElementsByTagName('sbl:frequencySwitching')[0].firstChild.data,
            #parent.getElementsByTagName('sbl:lO2Frequency')[0].firstChild.data,
            #parent.getElementsByTagName('sbl:lO2Frequency')[0].getAttribute('unit'),
            #parent.getElementsByTagName('sbl:weighting')[0].firstChild.data,
            #parent.getElementsByTagName('sbl:useUSB')[0].firstChild.data,
            #parent.getElementsByTagName('sbl:use12GHzFilter')[0].firstChild.data,
            #parent.getElementsByTagName('sbl:imageCenterFrequency')[0].firstChild.data,
            #parent.getElementsByTagName('sbl:imageCenterFrequency')[0].getAttribute('unit'),
            i.getAttribute('entityPartId'),
            i.getAttribute('baseBandName'),
            #i.getAttribute('sideBandPreference'),
            #i.getElementsByTagName('sbl:centerFrequency')[0].firstChild.data,
            #i.getElementsByTagName('sbl:lO2Frequency')[0].firstChild.data,
            #i.getElementsByTagName('sbl:lO2Frequency')[0].getAttribute('unit'),
            #i.getElementsByTagName('sbl:weighting')[0].firstChild.data,
            #i.getElementsByTagName('sbl:useUSB')[0].firstChild.data,
            #i.getElementsByTagName('sbl:use12GHzFilter')[0].firstChild.data,
            #i.getElementsByTagName('sbl:imageCenterFrequency')[0].firstChild.data,
            #i.getElementsByTagName('sbl:imageCenterFrequency')[0].getAttribute('unit')
        ))

    bb = pd.DataFrame(bbList)

    return bb,specs


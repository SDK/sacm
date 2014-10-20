# -*- coding: utf-8 -*-
__author__ = 'sdk'
from sacm import *
from xml.dom import minidom
import pandas as pd

asdmUID = ''


def getASDM(uid=None):
    asdmXML = GetXML(uid,'ASDM')
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
    return asdmList, pd.DataFrame(asdmList, columns=['table', 'numrows', 'typename', 'uid'])


def getMain(uid=None):
    mainXML = GetXML(uid,'Main')
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


def getScan(uid=None):
    scanXML = GetXML(uid,'Scan')
    scan = minidom.parseString(scanXML)
    scanList = list()
    rows = scan.getElementsByTagName('row')
    for i in rows:
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

    return pd.DataFrame(scanList, columns=['scanNumber', 'startTime', 'endTime', 'numSubscan',
                                         'scanIntent', 'calDataType', 'numField', 'fieldName', 'sourceName'])


def getSubScan(uid=None):
    subscanXML = GetXML(uid,'Subscan')
    #print subscanXML
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


def getSource(uid=None):
    sourceXML = GetXML(uid,'Source')
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


def getSpectralWindow(uid=None):
    spwXML = GetXML(uid,'SpectralWindow')
    spw = minidom.parseString(spwXML)
    spwList = list()
    rows = spw.getElementsByTagName('row')
    for i in rows:
        spwList.append((i.getElementsByTagName('spectralWindowId')[0].firstChild.data,
                        i.getElementsByTagName('basebandName')[0].firstChild.data,
                        i.getElementsByTagName('netSideband')[0].firstChild.data,
                        int(i.getElementsByTagName('numChan')[0].firstChild.data),
                        float(i.getElementsByTagName('refFreq')[0].firstChild.data),
                        i.getElementsByTagName('sidebandProcessingMode')[0].firstChild.data,
                        float(i.getElementsByTagName('totBandwidth')[0].firstChild.data),
                        #i.getElementsByTagName('chanFreqArray')[0].firstChild.data,
                        #i.getElementsByTagName('chanWidthArray')[0].firstChild.data,
                        #i.getElementsByTagName('effectiveBwArray')[0].firstChild.data,
                        i.getElementsByTagName('name')[0].firstChild.data,
                        #i.getElementsByTagName('resolutionArray')[0].firstChild.data,
                        i.getElementsByTagName('assocNature')[0].firstChild.data,
                        i.getElementsByTagName('assocSpectralWindowId')[0].firstChild.data.strip()))
    return pd.DataFrame(spwList, columns=['spectralWindowId', 'basebandName', 'netSideband', 'numChan',
                                         'refFreq', 'sidebandProcessingMode', 'totBandwidth', 'name',
                                         'assocNature', 'assocSpectralWindowId'])


def getField(uid=None):
    fieldXML = GetXML(uid,'Field')
    field = minidom.parseString(fieldXML)
    fieldList = list()
    rows = field.getElementsByTagName('row')
    for i in rows:
        fieldList.append((i.getElementsByTagName('fieldId')[0].firstChild.data,
                          i.getElementsByTagName('fieldName')[0].firstChild.data,
                          i.getElementsByTagName('numPoly')[0].firstChild.data,
                          #i.getElementsByTagName('delayDir')[0].firstChild.data,
                          #i.getElementsByTagName('phaseDir')[0].firstChild.data,
                          #i.getElementsByTagName('referenceDir')[0].firstChild.data,
                          int(i.getElementsByTagName('time')[0].firstChild.data),
                          i.getElementsByTagName('code')[0].firstChild.data,
                          i.getElementsByTagName('directionCode')[0].firstChild.data,
                          int(i.getElementsByTagName('sourceId')[0].firstChild.data)))
    return pd.DataFrame(fieldList, columns=['fieldId', 'fieldName', 'numPoly', 'time', 'code', 'directionCode', 'sourceId'])


def getSysCal(uid=None):
    syscalXML = GetXML(uid,'SysCal')
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

    target = pd.DataFrame(targetList, columns=['entityPartId','InstrumentSpec','FieldSource','ObsParameter'])


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
    return (bb,specs,target,phase,science,field)



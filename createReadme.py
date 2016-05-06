#!/bin/env python
import cx_Oracle
import sys
from MetaData import *

mous = sys.argv[1]
if '://' not in mous:
    mous = mous.replace('___','://').replace('_','/')
print "MOUS: ", mous


sql = '''select
al1.DOMAIN_ENTITY_ID as sb_uid,
al1.PARENT_OBS_UNIT_SET_STATUS_ID as mous_uid,
al2.PROJECTUID,
al2.PI_FULLNAME,
al2.PI_USERID,
al2.ASSOCIATEDEXEC,
al4.title,
al3.sb_name,
al3.REQUESTEDARRAY,
al3.MINACCEPTABLEANGRESOLUTION,
al3.MAXACCEPTABLEANGRESOLUTION,
al4.code
from
ALMA.SCHED_BLOCK_STATUS al1,
ALMA.BMMV_OBSPROPOSAL al2,
ALMA.BMMV_SCHEDBLOCK al3,
ALMA.BMMV_OBSPROJECT al4
where
al1.OBS_PROJECT_ID = al2.PROJECTUID
and al1.DOMAIN_ENTITY_ID = al3.ARCHIVE_UID
and al2.PROJECTUID = al4.PRJ_ARCHIVE_UID
and al1.PARENT_OBS_UNIT_SET_STATUS_ID = 'XXXXYYYY'
'''

sql = sql.replace('XXXXYYYY',mous)

try:
    conn = cx_Oracle.connect(databaseSCO)
    cursor = conn.cursor()
    cursor.execute(sql)
    row = cursor.fetchall()
except Exception as e:
    print e
    sys.exit(1)

sb_uid ,mous_uid ,prj_uid ,pi_fullname, pi_user, arc, title, sb_name, array, minAngRes, maxAngRes ,code = row[0]

sql2 = '''select al1.archive_uid Project_UID, x.*
from
ALMA.XML_OBSPROJECT_ENTITIES al1 ,
XMLTable('/*:ObsProject/*:ObsProgram/*:ObsPlan/*:ObsUnitSet/*:ObsUnitSet/*:ObsUnitSet'
     PASSING al1 .XML COLUMNS
    angular varchar2(672) PATH '*:DataProcessingParameters/*:angularResolution',
    SB_UID VARCHAR2(50) PATH '*:SchedBlockRef/@entityId'
    ) x
where al1.archive_uid = 'XXXXYYYY'
and x.SB_UID = 'ZZZZVVVV' '''

sql2 = sql2.replace('XXXXYYYY',prj_uid).replace('ZZZZVVVV',sb_uid)

try:
    cursor.execute(sql2)
    row = cursor.fetchall()
except Exception as e:
    print e
    sys.exit(1)

angular = row[0][1]

sql3 = '''select
extractvalue(al1.xml, '/*:SchedBlock/*:ScienceParameters/*:sensitivityGoal' ),
extractvalue(al1.xml, '/*:SchedBlock/*:ScienceParameters/*:sensitivityGoal/@unit' )
from ALMA.XML_SCHEDBLOCK_ENTITIES al1
where archive_uid = 'XXXXYYYY' '''

sql3 = sql3.replace('XXXXYYYY',sb_uid)

try:
    cursor.execute(sql3)
    row = cursor.fetchall()
except Exception as e:
    print e
    sys.exit(1)

sens,unit = row[0]

sql4 = '''with t1 as (select al1.PARENT_OBS_UNIT_SET_STATUS_ID as sg_uid
from ALMA.OBS_UNIT_SET_STATUS al1
where al1.STATUS_ENTITY_ID = 'ZZZZXXXXX')
select count(sg_uid)
from t1, ALMA.OBS_UNIT_SET_STATUS
where PARENT_OBS_UNIT_SET_STATUS_ID = t1.sg_uid '''

sql4 = sql4.replace('ZZZZXXXXX',mous_uid)

try:
    cursor.execute(sql4)
    row = cursor.fetchall()
except Exception as e:
    print e
    sys.exit(1)

count = row[0][0]
text = '''Atacama Large Millimeter/submillimeter Array (ALMA)

#####

Cycle: 3
Project code: %s
SB name: %s
PI name: %s (Username: %s)
Project title: %s
Configuration: %s
Proposed rms: %s %s
Proposed beam size: %s arcsec
CASA version used for reduction: 4.x
QA2 Result: PASS/SEMIPASS
Total Number of Member SBs in this OUS Group: %s
Comments from Reducer:
'''%(code,sb_name,pi_fullname,pi_user,title,array,sens,unit ,angular,count)

text += '''#####

This file describes the content of the tar file you have received. The
full data structure is inserted below.

At this stage, we are releasing data after completion of one SB (excuted
multiple times if required), so you will find only one member_ouss_id
directory.  This directory contains this README file and the following
directories:calibration, script, qa2, log, product.

- 'calibration' contains the files needed for calibration starting from
the initial ms to the fully calibrated data.
- 'script' contains the reduction scripts used to process the initial ms
to calibrated data, but also to obtain concatenated data (if more than
one execution) and imaging products.  There are usually several scripts
dealing with different parts of the processing.
In case the calibration was done by the automated pipeline, you will
also see the Pipeline Processing Request File (PPR).
The most important script for you is the "scriptForPI.py". See the
section "How to obtain the calibrated MeasurementSet (MS) for your data"
further below.
- 'product' contains the fits files of the selected image products.
These will not include all images of scientific value, but will indicate
the quality of the calibration and images.
- 'qa' contains the qa2 reports that show plots and text information
needed to assess the quality of the processing.  The resultant image
rms, compared with that proposed, is given. In case the calibration was
done by the automated pipeline, you will find the pipeline Weblog here.
- 'log' contains the CASA log files.

For more information see also the "ALMA QA2 Data Products" document
which is available for download from the ALMA Science Portal at
https://almascience.nrao.edu/documents-and-tools
and the ALMA Knowledgebase article on the QA2 pass/fail criteria at
https://help.almascience.org/index.php?/XX/Knowledgebase/Article/View/285
(where the XX is to be replaced by ea, eu, or na depending on your location).

#####

TOTAL POWER DATA

This section only concerns ALMA total power (TP) data. For ALMA 12m
and 7m interferometric data, please refer to the sections further below.

The ALMA TP data is reduced manually, using standard scripts, or using
the TP data reduction pipeline which performs calibration and imaging.
You can determine whether your data was reduced by Pipeline by
looking for a file "PPR...xml" in the "script" subdirectory (below
the directory containing this README). If such a file is present, your
data was pipeline-reduced.

TP datasets will often consist of many execution blocks (EBs). Each of
them was calibrated individually. Imaging is done on all calibrated data
together.

The images included in this delivery have a native frequency resolution
and a cell size of one ninths of beam size.
If you want to change them to your preferable frequency resolution and
cell size, import the delivered FITS cubes to CASA and regrid it using
the task imregrid.

One important aspect of the calibration is the conversion of the data
from K to Jy/beam. This is done per EB. For manually reduced data, the
values that were used are available at the end of each calibration script.
In case of pipeline-reduced data, the Jy per K conversion factors can be
found via the pipeline weblog in the "qa" directory or in the file
"jyperk.csv" under the "calibration" directory of this package.

The conversion factors were derived from the analysis of the associated
AMPCAL data from the same project. This analysis is done using standard
scripts or Pipeline. We are not providing those data by default to the
users, but in case you would be interested to have them, you are welcome
to contact the helpdesk of your region.


Pipeline-calibrated TP data

The following two paragraphs only describe the procedure for pipeline-
calibrated TP data.

If your TP dataset was pipeline-calibrated and you would like to
re-create the calibrated MeasurementSets, please read on in section
"How to obtain the calibrated MeasurementSet (MS) for your data".
Please note that processing may take a significant amount of time.
To know how long it will take,  please see the "Execution Duration"
which is shown on the top-page of the weblog.

If you want to perform baseline subtraction using your preferable
mask range rather than the pipeline-decided range, we recommend to
do it on the images using the task imcontsub or to do it using
the task sdbaseline during your own manual calibration (see
https://casaguides.nrao.edu/index.php?title=M100_Band3_SingleDish_4.3 ).


Manually calibrated TP data

The following three paragraphs only describe the procedure for manually
calibrated TP data.

At this stage, the QA report for manually reduced data is rudimentary.
If your TP data was reduced manually, please see the official CASA guide,
available at the following link:

https://casaguides.nrao.edu/index.php?title=M100_Band3_SingleDish_4.3

To regenerate the calibrated data, you will need to download the raw
data (ASDMs) from the ALMA archive, remove the '.asdm.sdm' extensions
and then run the scripts ('*.scriptForSDcalibration.py') in the scripts
folder. We recommend that you create an individual folder for each ASDM,
and calibrate each ASDM in its own folder.

For the imaging, we recommend you use the provided script, as it
contains certain values (e.g. beams) that must be set to a precise
value. You could run the script step-by-step, as for the calibration
script. Before doing that, you may need to update the paths to the
calibrated data, in the msNames variable near the top of the script.


#####

PRIMARY BEAM CORRECTION

The images included in this delivery are corrected for the primary beam (PB),
i.e. the dependence of the instruments sensitivity on direction within the FOV.

For each image, two files are being delivered:
  a) the  PB-corrected image (file name ending in ".pbcor.fits")
  b) the image of the PB which was used in the correction (ending in ".flux.fits")
The image noise was measured in the uncorrected image.
The corrected image (a) was then obtained by dividing the uncorrected image by
the PB image (b).
The uncorrected image can be recovered using the CASA task impbcor in mode "m":
impbcor(imagename='image.pbcor.fits', pbimage='image.flux.fits', mode='m',
        outfile='image.recovered')


#####

HOW TO OBTAIN THE CALIBRATED MEASUREMENTSET (MS) FOR YOUR DATA

In case you want to re-reduce your data yourself, you will need to
obtain the raw data in ASDM format from the request handler or
other server where it is staged for you (see your notification
email).

If you downloaded and untarred all available files for this delivery
as described in the notification email, then you will already see
(in addition to the directories shown in the tree listing above)
a directory "raw" containing your raw data in subdirectories
named "uid*.asdm.sdm" and no further action is necessary.

If you do not have a raw directory, yet, you will need to download
and untar the tar balls of the raw data belonging to this delivery
and make sure they are put into the "raw" directory in your
"member_ouss_..." directory.

Once the raw data is in place, cd into directory "script", start

   casapy --pipeline

and type

   execfile('scriptForPI.py')

(If you have not installed the CASA version with the ALMA pipeline
included, the "--pipeline" switch is not available.
Check in the "script" directory of your delivery package to see
if it contains a file named "PPR*.xml".
If there is no such file, you will be able to run the calibration
without the pipeline. Otherwise, you will have to install
the CASA version with pipeline.)

For more information on the execution of the pipeline please refer to
the ALMA Pipeline Quickstart Guide available at
https://almascience.nrao.edu/documents-and-tools/alma-science-pipeline-quickstart-guide-for-casa-4.5

Running the scriptForPI will execute the entire calibration procedure
and result in an MS or a set of MSs ready for imaging.

In case the data was processed using the automated pipeline,
scriptForPI.py will produce the calibrated MS(s) by running the
"casa_piperestorescript" which applies the packaged calibration
and flagging tables (rather then regenerating them).

If the casa_piperestorescript is not available (as can be the case
for pipeline-calibrated TP datasets), the scriptForPI will instead
run the entire calibration pipeline using the "casa_pipescript".

You can force the execution of the casa_pipescript instead of
the casa_piperestorescript by moving the casa_piperestorescript.py
out of the script directory. Rerunning the pipeline can be useful
if you want to tweak its parameters. Otherwise the restore is faster.

The calibrated MS(s) can then be processed with "scriptForImaging.py".

The "scriptForImaging.py" may partially be interactive (for masking)
and should be executed by copy and paste.

For TP MOUSs pipeline-calibrated, the scriptForImaging.py  is NOT provided.
You are able to find all used sdimaging task parameters in the CASA logs for stage 13 in the weblog.

The scriptForPI offers a "SPACESAVING" option to limit the disk space
usage during and after its execution. In order to make use of this,
the Python global variable SPACESAVING needs to be set before starting
the script, e.g. using

  SPACESAVING = N
  execfile('scriptForPI.py')

where N is an integer from 0 to 3 with the following meaning:
SPACESAVING = 0 same as not set (all intermediate MSs are kept)
            = 1 do not keep intermediate MSs named *.ms.split
            = 2 do not keep intermediate MSs named *.ms and *.ms.split
            = 3 do not keep intermediate MSs named *.ms, *.ms.split,
                and *.ms.split.cal (if possible)

With SPACESAVING=0, the required additional diskspace is up to 14 times
as large as the delivered data (products and rawdata) while with
SPACESAVING=3 (maximum savings), it is up to 6 times as large.
The script will estimate the required disk space and will not execute
if there is not sufficient free space available.

#####

'''

f = open('README','w')
f.write(text)
f.close()


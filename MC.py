__author__ = 'sagonzal'
from MetaData import *
import pandas as pd


def process():
    sb_list = list()
    band89 = pd.DataFrame()
    spectralScan = pd.DataFrame()

    projects = getProjectCodes(2)
    for prjuid, code in projects:
        schedblocks = getSBs(prjuid)
        for partid, sbuid in schedblocks:
            #print prjuid,code,sbuid, partid
            bb,specs,target,phase,science,field =  getSBData (sbuid)
            if len(field[field[1] == 'Ephemeris']) > 0:
                ephemeris = True
            else:
                ephemeris = False
            if len(specs[specs[5] == 'XX,YY,XY,YX']) > 0:
                polarization = True
            else:
                polarization = False

            df1 = pd.merge(science, target, left_on= 0, right_on = 'ObsParameter', how = 'inner', copy= False)
            if len(phase) > 0:
                df2 = pd.merge(phase, target, left_on= 0, right_on = 'ObsParameter', how = 'inner', copy= False)
                df3 = pd.merge(df1,df2 , right_on = 'InstrumentSpec', left_on = 'InstrumentSpec' , how = 'inner', copy = False)
                if len(df3) > 0:
                    sb_list.append((prjuid,code,sbuid, partid, 'Same PhaseCal Setup',ephemeris, polarization))
                else:
                    sb_list.append((prjuid,code,sbuid, partid, 'Different PhaseCal Setup',ephemeris, polarization))
            else:
                sb_list.append((prjuid,code,sbuid, partid, 'No PhaseCal (TP?)',ephemeris, polarization))

        band89 = pd.concat ([band89,pd.DataFrame(is_band89(prjuid))], ignore_index=True)
        spectralScan = pd.concat([spectralScan,pd.DataFrame(is_spectralscan(prjuid))],ignore_index=True)

    sbmous = pd.DataFrame(getSBMOUS())
    sbnames = pd.DataFrame(getSBNames())
    sbs = pd.DataFrame(sb_list)
    return (sbs,sbmous,band89,spectralScan,sbnames)


def main():
    sbs, sbmous, band89, spectralScan, sbnames = process()

    del spectralScan[0]
    del spectralScan[1]
    del band89[0]

    sbs = pd.merge(sbs, spectralScan , left_on = 3, right_on = 3, how='left', copy=False)
    sbs = pd.merge(sbs, band89, left_on = '2_x' ,right_on = 1, how = 'left', copy=False)
    sbmous.columns = [[0,'MOUS']]
    sbs = pd.merge(sbs,sbmous,left_on='2_x', right_on = 0, how = 'left', copy=False)
    sbnames.columns = [[0,'SB_NAME']]
    sbs = pd.merge(sbs,sbnames, left_on = '2_x', right_on = 0, how = 'left', copy=False)

    sbs = sbs.fillna('')
    sbs['Pipeline'] = sbs.apply(lambda x: True if x[4] == 'Same PhaseCal Setup' else False, axis = 1)
    sbs['Pipeline'] = sbs.apply(lambda x: False if 'RB_08' in x[2] else x['Pipeline'] , axis = 1)
    sbs['Pipeline'] = sbs.apply(lambda x: False if 'RB_09' in x[2] else x['Pipeline'] , axis = 1)
    sbs['Pipeline'] = sbs.apply(lambda x: False if x[5] == True else x['Pipeline'] , axis = 1)
    sbs['Pipeline'] = sbs.apply(lambda x: False if x[6] == True else x['Pipeline'] , axis = 1)
    sbs['SpectralScan'] = sbs.apply(lambda x: True if 'scan' in x['2_y'] else False , axis =1)
    final = sbs[['1_x','0_x','MOUS','SB_NAME','2_x','Pipeline',4,'SpectralScan',2,5,6]]
    final.columns = ['PRJ_CODE','PRJ_UID','MOUS','SB_NAME','SB_UID','Pipeline','PhaseSetup','SpectralScan','BAND','Ephemeris','Polarization']



    to_html = open('pipeline.html','w')
    to_html.write('<html><head></head><body>'+final.to_html()+'</body></html>')
    to_html.close()

    to_csv = open('pipeline.csv','w')
    to_csv.write(final.to_csv(sep='\t'))
    to_csv.close()

if __name__ == "__main__":
    main()


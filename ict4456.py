__author__ = 'sagonzal'
from MetaData import *

def checkOrder(sb_uid=None):
    a,b = getSB_spectralconf(sb_uid)
    baseband = a[[1,2]]
    baseband.columns = [['partId','BB']]
    spw = b[[0,3,4]]
    spw.columns = [['spwId','SB_UID','partId']]

    df = pd.merge(baseband,spw, left_on='partId', right_on='partId',copy=False )

    c = df.groupby('spwId')

    for name,group in c:
        unordered = list()
        ordered = list()
        i = c.get_group(name)
        values = i['BB'].values
        for j in values:
            unordered.append(j)
            ordered.append(j)

        ordered.sort()
        #print ordered
        #print unordered

        if unordered != ordered:
            return False
    return True


orcl = cx_Oracle.connect(database)
cursor = orcl.cursor()
projects = list()

sql = """select al1.DOMAIN_ENTITY_ID,al1.OBS_PROJECT_ID
from ALMA.SCHED_BLOCK_STATUS al1,
  ALMA.BMMV_OBSPROJECT al2
where
  (al2.code like '2011._.%._' or al2.code like '2012._.%._' or al2.code like '2013._.%._')
  and al1.OBS_PROJECT_ID = al2.PRJ_ARCHIVE_UID
order by 2 desc"""

cursor.execute(sql)

for i,j in cursor:
    projects.append([i,j])

df = pd.DataFrame(projects)
df.columns = [['SB_UID','PRJ_UID']]
df['ICT'] = df.apply(lambda x: checkOrder(x['SB_UID']) , axis = 1)

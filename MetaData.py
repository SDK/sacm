__author__ = 'sagonzal'
from checker import *

uid = 'uid://A002/X899169/X1179'
asdmDict = dict()
asdmList, asdm = getASDM(uid)

for i in asdmList:
    asdmDict[i[0].strip()] = i[3].strip()


def isNullState():
    main = getMain(asdmDict['Main'])
    main['null'] = main.apply(lambda x: True if 'null' in x['stateId'] else False, axis = 1)
    if len(main['null'].unique()) > 1:
        return True
    else:
        return False

def isValidUID():
    for k,v in asdmDict.iteritems():
        if '/X0/X0/X0' in v:
            return True
    return False


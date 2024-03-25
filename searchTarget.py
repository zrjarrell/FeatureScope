import pandas as pd
import sqlite3

def searchTarget(target, dataframe, esi):
    foundMatch = False
    if isinstance(dataframe, str):
        dataframe = pd.read_csv(dataframe, header=0, sep='\t')
    if esi == "pos":
        adductDict = target.posAdductMass
    elif esi == "neg":
        adductDict = target.negAdductMass
    resultList = []
    for adduct in adductDict:
        matches = dataframe[(dataframe["mz"] < adductDict[adduct][3]) & (dataframe["mz"] > adductDict[adduct][2])]
        if len(matches.index) > 0:
            foundMatch = True
            for res in matches.index:
                workingRow = matches.loc[res].copy()
                result = {k: workingRow[k] for k in matches.columns}
                result["theoreticalMZ"] = adductDict[adduct][0]
                result["adductForm"] = adductDict[adduct][1]
                result["ppmError"] = (workingRow["mz"] - adductDict[adduct][0])/adductDict[adduct][0] * 1000000
                resultList += [result]
    if foundMatch:
        matchDF = pd.DataFrame.from_dict(resultList)
        leadingColumns = ["theoreticalMZ", "adductForm", "ppmError"]
        matchDF = matchDF[leadingColumns + [col for col in matchDF.columns if col not in leadingColumns]]
    else:
        matchDF = "No matches"
    return matchDF

def checkForDbTable(cur, targetList):
    res = cur.execute("SELECT name FROM sqlite_master")
    tables = []
    for i in res.fetchall():
        tables += [str(i[0])]
    for target in targetList:
        if target.id not in tables:
            print(target.id)
            cur.execute("CREATE TABLE " + target.id + "(studyPath, esiMode, matches)")


def searchDataframe(con, cur, targetList, dfPath, esi):
    dataframe = pd.read_csv(dfPath, header=0, sep='\t')
    for target in targetList:
        matches = searchTarget(target, dataframe, esi)
        if not isinstance(matches, str):
            matches = pd.DataFrame.to_string(matches)
        cur.execute("INSERT INTO "+target.id+""" VALUES ('"""+dfPath+"""', '"""+esi+"""', '"""+matches+"""')""")
    con.commit()
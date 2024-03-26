import pandas as pd

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
            cur.execute("CREATE TABLE " + target.id + "_detectedFeatures(featureID TEXT NOT NULL, studyPath TEXT NOT NULL, esiMode TEXT NOT NULL, theoreticalMZ REAL NOT NULL, adductForm TEXT NOT NULL, ppmError REAL NOT NULL, mz REAL NOT NULL, time REAL NOT NULL)")
            cur.execute("CREATE TABLE " + target.id + "_sampleIntensities(featureID TEXT NOT NULL, sampleLabel TEXT NOT NULL, intensity REAL NOT NULL)")

def makeFeatureID(i):
    lead = 8 - len(str(i))
    featureNum = "feature" + "0" * lead + str(i)
    return featureNum

def searchDataframe(con, cur, targetList, dfPath, esi):
    dataframe = pd.read_csv(dfPath, header=0, sep='\t')
    for target in targetList:
        matches = searchTarget(target, dataframe, esi)
        if not isinstance(matches, str):
            print(matches)
            cur.execute("SELECT * FROM " + target.id + "_detectedFeatures")
            featureNumber = len(cur.fetchall()) + 1
            for i in matches.index:
                featureID = makeFeatureID(featureNumber)
                insertQuery = "INSERT INTO " + target.id + "_detectedFeatures (featureID, studyPath, esiMode, theoreticalMZ, adductForm, ppmError, mz, time) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
                dataTuple = (featureID, dfPath, esi, matches.loc[i, "theoreticalMZ"], matches.loc[i, "adductForm"], matches.loc[i, "ppmError"], matches.loc[i, "mz"], matches.loc[i, "time"])
                cur.execute(insertQuery, dataTuple)
                insertQuery = "INSERT INTO " + target.id + "_sampleIntensities (featureID, sampleLabel, intensity) VALUES (?, ?, ?)"
                for j in matches.columns[5:]:
                    if j in ['mz.min', 'mz.max', 'NumPres.All.Samples', 'NumPres.Biological.Samples', 'median_CV', 'Qscore', 'Max.Intensity', 'PeakScore']:
                        pass
                    else:
                        cur.execute(insertQuery, (featureID, j, matches.loc[i, j]))
                featureNumber += 1
    con.commit()
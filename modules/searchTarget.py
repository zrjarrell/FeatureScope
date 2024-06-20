import pandas as pd
import json
from modules.utilityFunctions import progressBar

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

def makeDbTables(con, cur):
    cur.execute("CREATE TABLE detectedFeatures(targetID TEXT NOT NULL, featureID TEXT NOT NULL, studyPath TEXT NOT NULL, esiMode TEXT NOT NULL, theoreticalMZ REAL NOT NULL, adductForm TEXT NOT NULL, ppmError REAL NOT NULL, mz REAL NOT NULL, time REAL NOT NULL)")
    cur.execute("CREATE TABLE sampleIntensities(featureID TEXT NOT NULL, sampleLabel TEXT NOT NULL, intensity REAL NOT NULL)")
    con.commit()

# def makeDbTable(cur, targetList):
#     res = cur.execute("SELECT name FROM sqlite_master")
#     tables = []
#     for i in res.fetchall():
#         tables += [str(i[0])]
#     for target in targetList:
#         if target.id + "_detectedFeatures" not in tables:
#             print(target.id)
#             cur.execute("CREATE TABLE " + target.id + "_detectedFeatures(featureID TEXT NOT NULL, studyPath TEXT NOT NULL, esiMode TEXT NOT NULL, theoreticalMZ REAL NOT NULL, adductForm TEXT NOT NULL, ppmError REAL NOT NULL, mz REAL NOT NULL, time REAL NOT NULL)")
#             cur.execute("CREATE TABLE " + target.id + "_sampleIntensities(featureID TEXT NOT NULL, sampleLabel TEXT NOT NULL, intensity REAL NOT NULL)")

def makeFeatureID(i):
    lead = 10 - len(str(i))
    featureNum = "feature" + "0" * lead + str(i)
    return featureNum

def addDbFeature(cur, target, featureID, dfPath, esi, matches, matchIndex):
    insertQuery = "INSERT INTO detectedFeatures (targetID, featureID, studyPath, esiMode, theoreticalMZ, adductForm, ppmError, mz, time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    dataTuple = (target.id, featureID, dfPath, esi, matches.loc[matchIndex, "theoreticalMZ"], matches.loc[matchIndex, "adductForm"], matches.loc[matchIndex, "ppmError"], matches.loc[matchIndex, "mz"], matches.loc[matchIndex, "time"])
    cur.execute(insertQuery, dataTuple)

def addSampleMeasures(cur, featureID, matches, matchIndex):
    insertQuery = "INSERT INTO sampleIntensities (featureID, sampleLabel, intensity) VALUES (?, ?, ?)"
    for i in matches.columns[5:]:
        if i in ['mz.min', 'mz.max', 'NumPres.All.Samples', 'NumPres.Biological.Samples', 'median_CV', 'Qscore', 'Max.Intensity', 'PeakScore']:
            pass
        else:
            cur.execute(insertQuery, (featureID, i, matches.loc[matchIndex, i]))

def searchDataframe(con, cur, targetList, dfPath, esi, studyNum, studyTotal, featureNumber, badPaths):
    try:
        dataframe = pd.read_csv(dfPath, header=0, sep='\t')
        targetCounter = 1
        for target in targetList:
            progressBar(studyNum, studyTotal, targetCounter, len(targetList))
            matches = searchTarget(target, dataframe, esi)
            if not isinstance(matches, str):
                for i in matches.index:
                    featureID = makeFeatureID(featureNumber)
                    addDbFeature(cur, target, featureID, dfPath, esi, matches, i)
                    addSampleMeasures(cur, featureID, matches, i)
                    featureNumber += 1
            targetCounter += 1
        return featureNumber
    except FileNotFoundError:
        badPaths += [dfPath]
    #con.commit()

def searchStudyList(con, cur, studyDictPath, targets, esi):
    badPaths = []
    cur.execute("SELECT * FROM detectedFeatures")
    featureNumber = len(cur.fetchall()) + 1
    studyDict = json.load(open(studyDictPath))
    for i in range(0, len(studyDict[esi])):
        featureNumber = searchDataframe(con, cur, targets, studyDict[esi][i], esi, i+1, len(studyDict[esi]), featureNumber, badPaths) or featureNumber
    con.commit()
    return badPaths

# def addDbFeature(cur, target, featureID, dfPath, esi, matches, matchIndex):
#     insertQuery = "INSERT INTO " + target.id + "_detectedFeatures (featureID, studyPath, esiMode, theoreticalMZ, adductForm, ppmError, mz, time) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
#     dataTuple = (featureID, dfPath, esi, matches.loc[matchIndex, "theoreticalMZ"], matches.loc[matchIndex, "adductForm"], matches.loc[matchIndex, "ppmError"], matches.loc[matchIndex, "mz"], matches.loc[matchIndex, "time"])
#     cur.execute(insertQuery, dataTuple)

# def addSampleMeasures(cur, target, featureID, matches, matchIndex):
#     insertQuery = "INSERT INTO " + target.id + "_sampleIntensities (featureID, sampleLabel, intensity) VALUES (?, ?, ?)"
#     for i in matches.columns[5:]:
#         if i in ['mz.min', 'mz.max', 'NumPres.All.Samples', 'NumPres.Biological.Samples', 'median_CV', 'Qscore', 'Max.Intensity', 'PeakScore']:
#             pass
#         else:
#             cur.execute(insertQuery, (featureID, i, matches.loc[matchIndex, i]))

# def searchDataframe(con, cur, targetList, dfPath, esi, studyNum, studyTotal):
#     dataframe = pd.read_csv(dfPath, header=0, sep='\t')
#     targetCounter = 1
#     for target in targetList:
#         progressBar(studyNum, studyTotal, targetCounter, len(targetList))
#         matches = searchTarget(target, dataframe, esi)
#         if not isinstance(matches, str):
#             cur.execute("SELECT * FROM " + target.id + "_detectedFeatures")
#             featureNumber = len(cur.fetchall()) + 1
#             for i in matches.index:
#                 featureID = makeFeatureID(featureNumber)
#                 addDbFeature(cur, target, featureID, dfPath, esi, matches, i)
#                 addSampleMeasures(cur, target, featureID, matches, i)
#                 featureNumber += 1
#         targetCounter += 1
#     #con.commit()

# def searchStudyList(con, cur, studyDict, targets, esi):
#     for i in range(0, len(studyDict[esi])):
#         searchDataframe(con, cur, targets, studyDict[esi][i], esi, i+1, len(studyDict[esi]))
#     con.commit()
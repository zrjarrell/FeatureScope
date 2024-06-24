import pandas as pd
from shutil import copyfile

def importChemicalLibrary(cur, library):
    for i in library.index:
        try:
            pmid = str(int(library.loc[i, "referencePMID"]))
        except ValueError:
            pmid = library.loc[i, "referencePMID"]
        insertQuery = "INSERT INTO targetChemicals (targetID, compoundName, neutralMonoisotopicMass, pubchemCID, modification, referencePMID) VALUES (?, ?, ?, ?, ?, ?)"
        dataTuple = (library.loc[i, "targetID"], library.loc[i, "compoundName"], library.loc[i, "neutralMonoisotopicMass"], str(library.loc[i, "pubchemCID"]),
                     library.loc[i, "modification"], pmid)
        cur.execute(insertQuery, dataTuple)

def makeDbTables(con, cur, library):
    cur.execute("CREATE TABLE detectedFeatures(targetID TINYTEXT NOT NULL, featureID TINYTEXT NOT NULL, studyID TINYTEXT NOT NULL, featureTablePath TEXT NOT NULL, esiMode TINYTEXT NOT NULL, theoreticalMZ REAL NOT NULL, adductForm TINYTEXT NOT NULL, ppmError REAL NOT NULL, mz REAL NOT NULL, time REAL NOT NULL)")
    cur.execute("CREATE TABLE sampleIntensities(featureID TINYTEXT NOT NULL, sampleLabel TEXT NOT NULL, intensity REAL NOT NULL)")
    cur.execute("CREATE TABLE targetChemicals(targetID TINYTEXT PRIMARY KEY, compoundName TEXT NOT NULL, neutralMonoisotopicMass REAL NOT NULL, pubchemCID TINYTEXT NOT NULL, modification TEXT, referencePMID TINYTEXT)")
    cur.execute("CREATE TABLE studies(studyID TINYTEXT PRIMARY KEY, majorPath TEXT NOT NULL, organism TINYTEXT, specimen TINYTEXT, instrument TINYTEXT, design TEXT, notes TEXT)")
    if isinstance(library, str):
        library = pd.read_csv(library, header=0, sep='\t')
    importChemicalLibrary(cur, library)
    con.commit()

def savePreviousVersions(ignoreArray=[]):
    paths = ['./targetDatabase.db', './mainPaths.json', './old5ppmPaths.json', './old10ppmPaths.json']
    for path in paths:
        if path not in ignoreArray:
            copyfile(path, './previousVersions' + path[1:])
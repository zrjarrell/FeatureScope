import buildTargets
import findExtracts
import searchTarget
import sqlite3

#read new target library
newTargets = buildTargets.getNewTargets()

#open db
con = sqlite3.connect("./targetDatabase.db")
cur = con.cursor()

#search 5 ppm data
newTargets5ppm = buildTargets.makeTargetChemicals(newTargets)
buildTargets.setTargetRanges(newTargets5ppm, 5)

searchTarget.checkForDbTable(cur, newTargets5ppm)

mainPaths = findExtracts.openFTpaths("./mainPaths.json")
old5ppmPaths = findExtracts.openFTpaths("./old5ppmPaths.json")

all5ppmPaths = {"current": mainPaths, "old": old5ppmPaths}
for pathlist in all5ppmPaths:
    print(f"Searching {pathlist} 5 ppm extracted data repository.\n\tSearching positive data.")
    searchTarget.searchStudyList(con, cur, all5ppmPaths[pathlist], newTargets5ppm, "pos")
    print(f"Searching {pathlist} 5 ppm extracted data repository.\n\tSearching negative data.")
    searchTarget.searchStudyList(con, cur, all5ppmPaths[pathlist], newTargets5ppm, "neg")

#search 10 ppm data
newTargets10ppm = buildTargets.makeTargetChemicals(newTargets)
buildTargets.setTargetRanges(newTargets10ppm, 10)

old10ppmPaths = findExtracts.openFTpaths("./old10ppmPaths.json")

print(f"Searching old 10 ppm extracted data repository.\n\tSearching positive data.")
searchTarget.searchStudyList(con, cur, old10ppmPaths, newTargets10ppm, "pos")
print(f"Searching old 10 ppm extracted data repository.\n\tSearching negative data.")
searchTarget.searchStudyList(con, cur, old10ppmPaths, newTargets10ppm, "neg")

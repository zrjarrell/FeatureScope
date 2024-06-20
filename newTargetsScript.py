import modules.buildTargets as buildTargets
import modules.findExtracts as findExtracts
import modules.searchTarget as searchTarget
import sqlite3

#read new target library
newTargets = buildTargets.getNewTargets()

#open db
con = sqlite3.connect("./targetDatabase.db")
cur = con.cursor()

#search 5 ppm data
newTargets5ppm = buildTargets.makeTargetChemicals(newTargets)
buildTargets.setTargetRanges(newTargets5ppm, 5)

mainPaths = "./mainPaths.json"
old5ppmPaths = "./old5ppmPaths.json"

badPaths = {}
all5ppmPaths = {"current": mainPaths, "old": old5ppmPaths}
for pathlist in all5ppmPaths:
    badPaths[pathlist + '5ppm'] = {}
    print(f"Searching {pathlist} 5 ppm extracted data repository.\n\tSearching positive data.")
    badPaths[pathlist + '5ppm']['pos'] = searchTarget.searchStudyList(con, cur, all5ppmPaths[pathlist], newTargets5ppm, "pos")
    print(f"Searching {pathlist} 5 ppm extracted data repository.\n\tSearching negative data.")
    badPaths[pathlist + '5ppm']['neg'] = searchTarget.searchStudyList(con, cur, all5ppmPaths[pathlist], newTargets5ppm, "neg")

#search 10 ppm data
newTargets10ppm = buildTargets.makeTargetChemicals(newTargets)
buildTargets.setTargetRanges(newTargets10ppm, 10)

old10ppmPaths = "./old10ppmPaths.json"

badPaths['old10ppm'] = {}
print(f"Searching old 10 ppm extracted data repository.\n\tSearching positive data.")
badPaths['old10ppm']['pos'] = searchTarget.searchStudyList(con, cur, old10ppmPaths, newTargets10ppm, "pos")
print(f"Searching old 10 ppm extracted data repository.\n\tSearching negative data.")
badPaths['old10ppm']['neg'] = searchTarget.searchStudyList(con, cur, old10ppmPaths, newTargets10ppm, "neg")

#remove bad paths from path libraries
print("Removing bad paths from path library.")
editLists = [mainPaths, old5ppmPaths, old10ppmPaths]
removalKeys = ['current5ppm', 'old5ppm', 'old10ppm']

for i in range(0, 3):
    for esi in ['pos', 'neg']:
        if len(badPaths[removalKeys[i]][esi]) > 0:
            findExtracts.removeMissingPaths(badPaths[removalKeys[i]], editLists[i], esi)
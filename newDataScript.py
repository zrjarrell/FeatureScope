import json
import sqlite3
import modules.manageExtracts as manageExtracts
import modules.buildTargets as buildTargets
import modules.searchTarget as searchTarget
from modules.dbManagement import savePreviousVersions

savePreviousVersions()

#search current directories to list
config = json.load(open('./config.json'))
mainRepo = config["repos"]["mainRepos"]
patterns = config["featureTableNamePatterns"]

print("Searching current repos for new data. This may take several minutes.")
currentMainRepoPaths = manageExtracts.getFeatureTablePaths(mainRepo, patterns)

#find list values not in mainPaths or blacklist and store in newPaths list
mainPathsUnsorted = json.load(open('./pathsNotSortedByMethod/mainPathsUnsorted.json'))
blacklistedPaths = json.load(open('./pathsNotSortedByMethod/blacklistedPaths.json'))

newMainRepoPaths = []
for path in currentMainRepoPaths:
    if path not in mainPathsUnsorted and path not in blacklistedPaths:
        newMainRepoPaths += [path]

#update mainPathsUnsorted.json
mainPathsUnsorted += newMainRepoPaths

json.dump(mainPathsUnsorted, open('./pathsNotSortedByMethod/mainPathsUnsorted.json', 'w'), indent=4)

#sort newly found featureTable paths by method
newMainPathsSorted = manageExtracts.splitPathsByMethod(newMainRepoPaths)

#update mainPaths.json with newly found paths
mainPaths = json.load(open('./mainPaths.json'))
for key in mainPaths:
    mainPaths[key] += newMainPathsSorted[key]

json.dump(mainPaths, open('./mainPaths.json', 'w'), indent=4)
json.dump(newMainPathsSorted, open('./previousVersions/newestMainSearchBackup.json', 'w'), indent=4)

#######search newPaths list for targets and update database
#open db
con = sqlite3.connect("./targetDatabase.db")
cur = con.cursor()

#build 5 ppm targets
targets5ppm = buildTargets.makeTargetChemicals(con)
buildTargets.setTargetRanges(targets5ppm, 5)

badPaths = {}
new5ppmPaths = {"new": './previousVersions/newestMainSearchBackup.json'}
for pathlist in new5ppmPaths:
    print(f"Searching {pathlist} 5 ppm extracted data repository.\n\tSearching positive data.")
    badPaths['pos'] = searchTarget.searchStudyList(con, cur, new5ppmPaths[pathlist], targets5ppm, "pos")
    print(f"Searching {pathlist} 5 ppm extracted data repository.\n\tSearching negative data.")
    badPaths['neg'] = searchTarget.searchStudyList(con, cur, new5ppmPaths[pathlist], targets5ppm, "neg")

#remove any bad paths from path libraries
print("Removing bad paths from path library.")
for esi in ['pos', 'neg']:
    if len(badPaths[esi]) > 0:
        manageExtracts.removeMissingPaths(badPaths, './mainPaths.json', esi)
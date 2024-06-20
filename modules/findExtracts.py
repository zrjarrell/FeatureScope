import os
import json
import pandas as pd
import math

def getRepositoryInfo():
    repoInfo = pd.read_csv("./repositoryInfo.txt", header=0, sep="\t")
    mainRepo = []
    old5ppmRepo = []
    old10ppmRepo = []
    patterns = []
    for path in repoInfo["mainRepositories"]:
        try:
            math.isnan(path)
        except TypeError:
            mainRepo += [path]
    for path in repoInfo["old5ppmRepos"]:
        try:
            math.isnan(path)
        except TypeError:
            old5ppmRepo += [path]
    for path in repoInfo["old10ppmRepos"]:
        try:
            math.isnan(path)
        except TypeError:
            old10ppmRepo += [path]
    for path in repoInfo["featureTablePatterns"]:
        try:
            math.isnan(path)
        except TypeError:
            patterns += [path]
    return mainRepo, old5ppmRepo, old10ppmRepo, patterns

def getFeatureTablePaths(repos, patterns):
    filepaths = []
    for repo in repos:
        dirTree = os.walk(repo)
        for (dirpath, dirs, files) in dirTree:
            for filename in files:
                fname = os.path.join(dirpath, filename)
                if filename in patterns:
                    if list(pd.read_csv(fname, header=0, sep="\t").columns[0:2]) == ['mz', 'time']:
                        filepaths += [fname]
    return filepaths

def splitPathsByMethod(pathList):
    posList = []
    negList = []
    unkList = []
    for filePath in pathList:
        path = filePath.lower()
        if "c18neg" in path:
            negList += [filePath]
        elif "hilicpos" in path or "c18pos" in path or "ae" in path:
            posList += [filePath]
        elif "neg" in path:
            negList += [filePath]
        elif "pos" in path:
            posList += [filePath]
        else:
            unkList += [filePath]
    for i in range(len(unkList)-1, -1, -1):
        print(f'Number of paths remaining to sort: {i+1}')
        print(unkList[i] + "\n")
        response = input("Pos(p) or Neg(n)? ")
        if response == "p":
            posList += [unkList.pop(i)]
        elif response == "n":
            negList += [unkList.pop(i)]
        else:
            pass
    return {"pos": posList, "neg": negList, "unassigned": unkList}

def removeMissingPaths(removalList, wholeListJSONPath, esi):
    #update method sorted jsons by removing dud paths
    editedList = []
    wholeList = json.load(open(wholeListJSONPath))
    for path in wholeList[esi]:
        if path not in removalList[esi]:
            editedList += [path]
    wholeList[esi] = editedList
    #update non-method sorted jsons by removing dud paths
    unsortedWholeListJSONPath = './pathsNotSortedByMethod/' + wholeListJSONPath[2:-5] + 'Unsorted.json'
    unsortedEditedList = []
    unsortedWholelist = json.load(open(unsortedWholeListJSONPath))
    for path in unsortedWholelist:
        if path not in removalList:
            unsortedEditedList += [path]
    json.dump(wholeList, open(wholeListJSONPath, 'w'), indent=4)
    json.dump(unsortedEditedList, open(unsortedWholeListJSONPath, 'w'), indent=4)



#mainRepo, old5ppmRepo, old10ppmRepo, patterns = getRepositoryInfo()



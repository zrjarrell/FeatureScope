import os
import json
import pandas as pd

def getRepositoryInfo():
    repoInfo = pd.read_csv("./repositoryInfo.txt", header=0, sep="\t")
    repoInfo.fillna("", inplace=True)
    mainRepo = []
    old5ppmRepo = []
    old10ppmRepo = []
    patterns = []
    for path in repoInfo["mainRepositories"]:
        if path != "":
            mainRepo += [path]
    for path in repoInfo["old5ppmRepos"]:
        if path != "":
            old5ppmRepo += [path]
    for path in repoInfo["old10ppmRepos"]:
        if path != "":
            old10ppmRepo += [path]
    for path in repoInfo["featureTablePatterns"]:
        if path != "":
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

def saveFTpaths(dict, filename):
    with open(filename, "w") as fileObject:
        json.dump(dict, fileObject)
    fileObject.close()

def openFTpaths(filepath):
    f = open(filepath)
    return json.load(f)

#mainRepo, old5ppmRepo, old10ppmRepo, patterns = getRepositoryInfo()



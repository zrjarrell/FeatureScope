import findExtracts
import buildTargets
import sqlite3
import searchTarget

mainPaths = findExtracts.openFTpaths("./mainPaths.json")

targets = buildTargets.makeTargetChemicals("./targetList.txt")
buildTargets.setTargetRanges(targets, 5)


con = sqlite3.connect("./targetDatabase.db")
cur = con.cursor()

searchTarget.checkForDbTable(cur, targets)

searchTarget.searchStudyList(con, cur, mainPaths, targets, "neg")
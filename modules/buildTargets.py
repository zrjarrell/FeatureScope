from modules.utilityFunctions import properRound
import pandas as pd
import numpy as np

class TargetChemical:
    def __init__(self, targetID, name, neutralMass, pubchemID, modification = "", reference = ""):
        self.id = targetID
        self.name = name
        self.pubchemID = str(pubchemID)
        self.neutralMass = neutralMass
        self.posAdductMass = {
            "M3H": [properRound((neutralMass/3) + 1.007276, 6), "M+3H"],
            "M2HNa": [properRound((neutralMass/3) + 8.334590, 6), "M+2H+Na"],
            "MH2Na": [properRound((neutralMass/3) + 15.7661904, 6), "M+H+2Na"],
            "M3Na": [properRound((neutralMass/3) + 22.989218, 6), "M+3Na"],
            "M2H": [properRound((neutralMass/2) + 1.007276, 6), "M+2H"],
            "MHNH4": [properRound((neutralMass/2) + 9.520550, 6), "M+H+NH4"],
            "MHNa": [properRound((neutralMass/2) + 11.998247, 6), "M+H+Na"],
            "MHK": [properRound((neutralMass/2) + 19.985217, 6), "M+H+K"],
            "MACN2H": [properRound((neutralMass/2) + 21.520550, 6), "M+ACN+2H"],
            "M2Na": [properRound((neutralMass/2) + 22.989218, 6), "M+2Na"],
            "M2ACN2H": [properRound((neutralMass/2) + 42.033823, 6), "M+2ACN+2H"],
            "M3ACN2H": [properRound((neutralMass/2) + 62.547097, 6), "M+3ACN+2H"],
            "MH": [properRound(neutralMass + 1.007276, 6), "M+H"],
            "MNH4": [properRound(neutralMass + 18.033823, 6), "M+NH4"],
            "MNa": [properRound(neutralMass + 22.989218, 6), "M+Na"],
            "MCH3OHH": [properRound(neutralMass + 33.033489, 6), "M+CH3OH+H"],
            "MK": [properRound(neutralMass + 38.963158, 6), "M+K"],
            "MACNH": [properRound(neutralMass + 42.033823, 6), "M+ACN+H"],
            "M2ACNH": [properRound(neutralMass + 83.060370, 6), "M+2ACN+H"],
            "M2Na-H": [properRound(neutralMass + 44.971160, 6), "M+2Na-H"],
            "MACNNa": [properRound(neutralMass + 64.015765, 6), "M+ACN+Na"],
            "M2K-H": [properRound(neutralMass + 76.919040, 6), "M+2K-H"],
            "2MH": [properRound((2*neutralMass) + 1.007276, 6), "2M+H"],
            "2MNH4": [properRound((2*neutralMass) + 18.033823, 6), "2M+NH4"],
            "2MNa": [properRound((2*neutralMass) + 22.989218, 6), "2M+Na"],
            "2MK": [properRound((2*neutralMass) + 38.963158, 6), "2M+K"],
            "2MACNH": [properRound((2*neutralMass) + 42.033823, 6), "2M+ACN+H"],
            "2MACNNa": [properRound((2*neutralMass) + 64.015765, 6), "2M+ACN+Na"],
            "M-H2OH": [properRound(neutralMass + 17.003289, 6), "M-H2O+H"]
            }
        self.negAdductMass = {
            "M3H": [properRound((neutralMass/3) - 1.007276, 6), "M-3H"],
            "M2H": [properRound((neutralMass/2) - 1.007276, 6), "M-2H"],
            "MH2OH": [properRound(neutralMass - 19.01839, 6), "M-H2O-H"],
            "MH": [properRound(neutralMass - 1.007276, 6), "M-H"],
            "M+Na2H": [properRound(neutralMass + 20.974666, 6), "M+Na-2H"],
            "MCl": [properRound(neutralMass + 34.969402, 6), "M+Cl"],
            "M+K2H": [properRound(neutralMass + 36.948606, 6), "M+K-2H"],
            "MFAH": [properRound(neutralMass + 44.998201, 6), "M+HCOO-H"],
            "MAcetH": [properRound(neutralMass + 59.013851, 6), "M+CH3COO"],
            "MBr": [properRound(neutralMass + 78.918885, 6), "M+Br"],
            "2MH": [properRound((2*neutralMass) - 1.007276, 6), "2M-H"],
            "2MFAH": [properRound((2*neutralMass) + 44.998201, 6), "2M+HCOO"],
            "2MAcetH": [properRound((2*neutralMass) + 59.013851, 6), "2M+CH3COO"],
            "3MH": [properRound((3*neutralMass) - 1.007276, 6), "3M-H"]
        }
        if modification == np.nan:
            modification = ""
        if reference == np.nan:
            reference = ""
        self.modification = modification
        self.referencePMID = str(reference)
    
    def setRanges(self, ppm):
        if not hasattr(self, "error"):
            self.error = ppm
            for i in ["posAdductMass", "negAdductMass"]:
                massList = getattr(self, i)
                for ion in massList:
                    theoreticalMass = massList[ion][0]
                    massList[ion].append(properRound(theoreticalMass - (theoreticalMass * ppm / 1000000), 6))
                    massList[ion].append(properRound(theoreticalMass + (theoreticalMass * ppm / 1000000), 6))
                setattr(self, i, massList)
        else:
            print(f"Error: Range of {self.error} ppm already set for this object. Rebuild target list if you wish to use a different magnitude of mass error.")

def makeTargetChemicals(library):
    if isinstance(library, str):
        library = pd.read_csv(library, header=0, sep="\t")
    targetChemicalList = []
    for i in library.index:
        targetChemicalList += [TargetChemical(library.loc[i, "target.id"],
                                              library.loc[i, "compound.name"],
                                              library.loc[i, "neutral.monoisotopic.mass"],
                                              library.loc[i, "pubchem.cid"],
                                              library.loc[i, "modification"],
                                              library.loc[i, "reference.pmid"])]
    return targetChemicalList

def setTargetRanges(targetChemicalList, ppm):
    for targetChemical in targetChemicalList:
        targetChemical.setRanges(ppm)

def getNewTargets():
    oldTargets = pd.read_csv("./targetList.txt", header=0, sep="\t")
    newTargets = pd.read_csv("./newTargets.txt", header=0, sep="\t")
    lastLabel = int(oldTargets.loc[len(oldTargets)-1, "target.id"].split('target')[1])
    targetIDs = []
    for i in newTargets.index:
        targetIDs += ['target' + ("0" * (6 - len(str(lastLabel+1))) + str(lastLabel+1))]
        lastLabel += 1
    newTargets.insert(0, "target.id", targetIDs, True)
    totalTargets = pd.concat([oldTargets, newTargets]).reset_index(drop=True)
    totalTargets.to_csv("./targetList.txt", sep="\t", index=False)
    newBlank = pd.DataFrame(columns = newTargets.columns[1:])
    newBlank.to_csv("newTargets.txt", sep="\t", index=False)
    return newTargets
import math
import re

from dataclasses import dataclass
from matplotlib import pyplot as plt
from turtle import clone, pd

# Mode 0 = Unprocessed, 1 = Processed
mode = 0

# File, ids map
if mode == 1:
    fileIds = {
        "mod_raycore_Paul.f90": 0,
        "RAY.f90": 1,
        "gnu_routines.f90": 2,
        "rayxml.f90": 3,
        "REFLEC_IN.f90": 4,
        "OEINPUT.f90": 5,
        "CRYSUB.f90": 6,
        "REFLEC.f90": 7,
        "RAYLIB.f90": 8,
        "OPTICS.f90": 9,
        "mod_raycore.f90": 10,
        "SOURCE.f90": 11,
        "OPTCON.f90": 12,
        "REFLEC_OUT.f90": 13,
        "REFLEC_CAL.f90": 14
    }
    pathPrefix = "../CCDTools/CodeBase/Preprocessed/"
else:
    fileIds = {
        "RAY.FOR": 0,
        "mod_raycore_Paul.f90": 1,
        "REFLEC_OUT.FOR": 2,
        "RAYLIB.FOR": 3,
        "OEINPUT.FOR": 4,
        "REFLEC_IN.FOR": 5,
        "rayxml.f90": 6,
        "OPTICS.FOR": 7,
        "REFLEC_CAL.FOR": 8,
        "SOURCE.FOR": 9,
        "OPTCON.FOR": 10,
        "CRYSUB.FOR": 11,
        "REFLEC.FOR": 12,
        "gnu_routines.for": 13,
        "mod_raycore.f90": 14
    }
    pathPrefix = "../CCDTools/CodeBase/Unprocessed/"


@dataclass
class Clone:
    # Class to hold the clone information
    fileID: int
    startLine: int
    endLine: int
    length: int


def readCCFinderResults(filename):
    filenames = []
    cloneSetList = []
    # Read in the results from the file into lists of clone classes
    with open(filename, 'r') as f:
        lines = f.readlines()

        # Skip the first few lines and read in files
        for i, line in enumerate(lines):
            if line.startswith("#source_files"):
                i += 1
                while not lines[i].startswith("#clone_sets"):
                    path = lines[i].split()[3]
                    name = re.split(r'[/\\]', path)[-1]
                    filenames.append(name)
                    i += 1
                i += 2  # Skip the first cloneID line
                break

        cloneSet = []
        for i in range(i, len(lines)):
            if lines[i].startswith("cloneID:"):
                cloneSetList.append(cloneSet)
                cloneSet = []
                continue
            else:
                line = re.split(r'[\s,:-]+', lines[i])
                line = list(filter(None, line))  # remove empty
                name = filenames[int(line[0])]
                fileID = fileIds[name]
                startLine = int(line[1])
                endLine = int(line[3])
                length = endLine - startLine + 1
                cloneSet.append(Clone(fileID, startLine, endLine, length))
    return cloneSetList


def readCPDResults(filename):
    cloneSetList = []
    # Read in the results from the file into lists of clone classes
    with open(filename, 'r') as f:
        lines = f.readlines()
        count = 0
        # Iterate over file and look for line starting with "Found a "
        for i, line in enumerate(lines):
            if line.startswith("Found a "):
                cloneSetList.append([])
                line = line.split()
                length = int(line[2])
                i += 1
                while lines[i].startswith("Starting at line "):
                    path = lines[i].split()[-1]
                    name = re.split(r'[/\\]', path)[-1]
                    fileID = fileIds[name]
                    startLine = int(lines[i].split()[3])
                    endLine = startLine + length - 1
                    cloneSetList[count].append(
                        Clone(fileID, startLine, endLine, length))
                    i += 1
                count += 1
    return cloneSetList

    pass


def readDuploResults(filename):
    # Read in the results from the file into lists of clone classes
    cloneSetList = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        count = 0
        cloneSet = []
        for line in lines:
            if line.startswith("/"):
                line = re.split(r'[/()]+', line)
                line = list(filter(None, line))  # remove empty
                line = line[0:-1]  # remove last element
                fileID = fileIds[line[-2]]
                startLine = int(line[-1])
                endLine = -1
                length = -1
                cloneSet.append(Clone(fileID, startLine, endLine, length))
            elif line.startswith("\n"):
                for i in range(len(cloneSet)):
                    cloneSet[i].length = count
                    cloneSet[i].endLine = cloneSet[i].startLine + \
                        cloneSet[i].length - 1
                cloneSetList.append(cloneSet)
                cloneSet = []
                count = 0
            else:
                count += 1
    return cloneSetList


def linesOfCode(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        count = 0
        for line in lines:
            count += 1
    return count


def cloneCount(cloneSetList: list):
    count = 0
    for cloneSet in cloneSetList:
        count += len(cloneSet)
    return count


def cloneLines(cloneSetList: list):
    count = 0
    for cloneSet in cloneSetList:
        for clone in cloneSet:
            count += clone.length
    return count


def averageCloneLength(cloneSetList: list):
    min = 100000000
    max = 0
    total = 0
    stdev = 0

    for cloneSet in cloneSetList:
        for clone in cloneSet:
            if clone.length < min:
                min = clone.length
            if clone.length > max:
                max = clone.length
            total += clone.length
    average = total / cloneCount(cloneSetList)
    for cloneSet in cloneSetList:
        for clone in cloneSet:
            stdev += (clone.length - average)**2
    stdev = math.sqrt(stdev / cloneCount(cloneSetList))
    return average, min, max, stdev


def clonePercentage(cloneSetList: list, filename):
    name = re.split(r'[/\\]', filename)[-1]
    cloneLines = 0
    for cloneSet in cloneSetList:
        for clone in cloneSet:
            if clone.fileID == fileIds[name]:
                cloneLines += clone.length
    return round(cloneLines / linesOfCode(filename) * 100, 2)


def areClose(a, b, threshold=5):
    return abs(a - b) <= threshold


def biggestCommonClone(cloneSetList1: list, cloneSetList2: list, cloneSetList3: list):
    biggest = [0, 0, 0]
    startLine = [0, 0, 0]
    fileID = [0, 0, 0]
    for cloneSet1 in cloneSetList1:
        for clone1 in cloneSet1:
            for cloneSet2 in cloneSetList2:
                for clone2 in cloneSet2:
                    if clone1.fileID == clone2.fileID and areClose(clone1.startLine, clone2.startLine) and areClose(clone1.endLine, clone2.endLine):
                        for cloneSet3 in cloneSetList3:
                            for clone3 in cloneSet3:
                                if clone1.fileID == clone3.fileID and areClose(clone1.startLine, clone3.startLine) and areClose(clone1.endLine, clone3.endLine):
                                    if clone1.length > biggest[0] and clone2.length > biggest[1] and clone3.length > biggest[2]:
                                        biggest[0] = clone1.length
                                        biggest[1] = clone2.length
                                        biggest[2] = clone3.length

                                        startLine[0] = clone1.startLine
                                        startLine[1] = clone2.startLine
                                        startLine[2] = clone3.startLine

                                        fileID[0] = clone1.fileID
                                        fileID[1] = clone2.fileID
                                        fileID[2] = clone3.fileID
    return biggest, startLine, fileID


def pairwiseAgreeForFile(cloneSetList1: list, cloneSetList2: list, filePath: str):
    # Total number of lines for file
    totalLines = 0
    with open(filePath, 'r') as f:
        lines = f.readlines()
        for line in lines:
            totalLines += 1

    lineIsClone1 = [False] * totalLines
    lineIsClone2 = [False] * totalLines
    cloneLines1 = 0
    cloneLines2 = 0
    commonCloneLines = 0
    for cloneSet1 in cloneSetList1:
        for clone1 in cloneSet1:
            if clone1.fileID == fileIds[filePath.split("/")[-1]]:
                for i in range(clone1.startLine, clone1.endLine + 1):
                    if not lineIsClone1[i]:
                        lineIsClone1[i] = True
                        cloneLines1 += 1

    for cloneSet2 in cloneSetList2:
        for clone2 in cloneSet2:
            if clone2.fileID == fileIds[filePath.split("/")[-1]]:
                for i in range(clone2.startLine, clone2.endLine + 1):
                    if not lineIsClone2[i]:
                        lineIsClone2[i] = True
                        cloneLines2 += 1

    if cloneLines1 == 0 and cloneLines2 == 0:
        return 100, 0, 0
    if cloneLines1 == 0:
        return 0, 0, cloneLines2
    if cloneLines2 == 0:
        return 0, round(cloneLines1 / totalLines * 100, 2), 0

    for i in range(totalLines):
        if lineIsClone1[i] and lineIsClone2[i]:
            commonCloneLines += 1

    agreement = round(commonCloneLines /
                      max(cloneLines1, cloneLines2) * 100, 2)

    cloneLinePercentage1 = round(cloneLines1 / totalLines * 100, 2)
    cloneLinePercentage2 = round(cloneLines2 / totalLines * 100, 2)

    return agreement, cloneLinePercentage1, cloneLinePercentage2


# Total agreement over all files
def totalAgreement(cloneSetList1: list, cloneSetList2: list):
    totalAgreement = 0
    totalFiles = 0
    for filePath in fileIds:
        agreement, _, _ = pairwiseAgreeForFile(
            cloneSetList1, cloneSetList2, pathPrefix + filePath)
        totalAgreement += agreement
        totalFiles += 1
    return round(totalAgreement / totalFiles, 2)


# Agreement for each file
def pairwiseAgreement(cloneSetList1: list, cloneSetList2: list):
    agreementList = []
    for filePath in fileIds:
        agreement, cloneLines1, cloneLines2 = pairwiseAgreeForFile(
            cloneSetList1, cloneSetList2, pathPrefix + filePath)
        agreementList.append((filePath, agreement, cloneLines1, cloneLines2))
    return agreementList


def checkCloneExists(cloneSetList: list, clone: Clone):
    for cloneSet in cloneSetList:
        for c in cloneSet:
            if c.fileID == clone.fileID and areClose(c.startLine, clone.startLine, 20) and areClose(c.endLine, clone.endLine, 20):
                return True
    return False


# Finds biggest outlier for first clone set list
def biggestOutlier(cloneSetList1: list, cloneSetList2: list, cloneSetList3: list):
    biggest = 0
    startLine = 0
    fileID = -1
    for cloneSet1 in cloneSetList1:
        for clone1 in cloneSet1:
            if clone1.length > biggest:
                if not checkCloneExists(cloneSetList2, clone1) and not checkCloneExists(cloneSetList3, clone1):
                    biggest = clone1.length
                    startLine = clone1.startLine
                    fileID = clone1.fileID

    return biggest, startLine, fileID


def printBiggestOutlier(cloneSetList1: list, cloneSetList2: list, cloneSetList3: list, name: str):
    biggest, startLine, fileID = biggestOutlier(
        cloneSetList1, cloneSetList2, cloneSetList3)
    print("Biggest outlier for " + name)
    print("\tLength: " + str(biggest))
    print("\tStart line: " + str(startLine))
    print("\tFile: " + str(fileID))
    print()


def fileCountLineDetections(cloneSetList: list, filePath: str):
    lines = 0
    with open(filePath, 'r') as f:
        for line in f.readlines():
            lines += 1

    lineCloneCount = [0] * lines
    for cloneSet in cloneSetList:
        for clone in cloneSet:
            if clone.fileID == fileIds[filePath.split("/")[-1]]:
                for i in range(clone.startLine, clone.endLine + 1):
                    lineCloneCount[i] += 1

    return lineCloneCount


def lineHeatmapCSV(cloneSetList1: list, cloneSetList2: list, cloneSetList3: list, filePath: str):
    lineCloneCount1 = fileCountLineDetections(cloneSetList1, filePath)
    lineCloneCount2 = fileCountLineDetections(cloneSetList2, filePath)
    lineCloneCount3 = fileCountLineDetections(cloneSetList3, filePath)

    with open("lineHeatmap.csv", 'w') as f:
        for i in range(len(lineCloneCount1)):
            f.write(str(i+1) + "," + str(lineCloneCount1[i]) + "," +
                    str(lineCloneCount2[i]) + "," + str(lineCloneCount3[i]) + "\n")


def main():
    # Read in the results from the three files
    if mode == 1:
        cloneSetListCC = readCCFinderResults(
            "./Results/Preprocessed/out_ccfsw.txt")
        cloneSetListCPD = readCPDResults("./Results/Preprocessed/out_pmd.txt")
        cloneSetListDuplo = readDuploResults(
            "./Results/Preprocessed/out_duplo.txt")
    else:
        cloneSetListCC = readCCFinderResults(
            "./Results/Unprocessed/out_ccfsw.txt")
        cloneSetListCPD = readCPDResults("./Results/Unprocessed/out_pmd.txt")
        cloneSetListDuplo = readDuploResults(
            "./Results/Unprocessed/out_duplo.txt")

    # Code base lines of code (total and per file)
    print("Lines of code")
    totalLines = 0
    fileLines = []
    for filePath in fileIds:
        lines = 0
        with open(pathPrefix + filePath, 'r') as f:
            for line in f.readlines():
                lines += 1
        totalLines += lines
        fileLines.append((filePath, lines))
    print("\tTotal: " + str(totalLines))
    print("\tPer file: " + str(fileLines))

    # Compare the results
    # Clone classes
    print("Clone classes:")
    print("\tCCFinder Results:" + str(len(cloneSetListCC)))
    print("\tCPD Results:" + str(len(cloneSetListCPD)))
    print("\tDuplo Results:" + str(len(cloneSetListDuplo)))

    # Compare the number of clones
    print("Clone counts:")
    print("\tCCFinder: " + str(cloneCount(cloneSetListCC)))
    print("\tCPD: " + str(cloneCount(cloneSetListCPD)))
    print("\tDuplo: " + str(cloneCount(cloneSetListDuplo)))

    # Compare the number of lines of code
    print("Lines of clones:")
    print("\tCCFinder: " + str(cloneLines(cloneSetListCC)))
    print("\tCPD: " + str(cloneLines(cloneSetListCPD)))
    print("\tDuplo: " + str(cloneLines(cloneSetListDuplo)))

    # Compare the average clone length
    print("Average clone length:")
    print("\tCCFinder: " + str(averageCloneLength(cloneSetListCC)))
    print("\tCPD: " + str(averageCloneLength(cloneSetListCPD)))
    print("\tDuplo: " + str(averageCloneLength(cloneSetListDuplo)))

    # Tool agreement over all files
    print("Tool agreement:")
    print("\tCCFinder vs CPD: " +
          str(totalAgreement(cloneSetListCC, cloneSetListCPD)))
    print("\tCCFinder vs Duplo: " +
          str(totalAgreement(cloneSetListCC, cloneSetListDuplo)))
    print("\tCPD vs Duplo: " +
          str(totalAgreement(cloneSetListCPD, cloneSetListDuplo)))

    # Tool agreement for each file
    print("Tool agreement for each file:")
    print("\tCCFinder vs CPD:")
    for filePath, agreement, cloneLines1, cloneLines2 in pairwiseAgreement(cloneSetListCC, cloneSetListCPD):
        print("\t\t" + filePath + ": " + str(agreement) +
              " (" + str(cloneLines1) + ", " + str(cloneLines2) + ")")
    print("\tCCFinder vs Duplo:")
    for filePath, agreement, cloneLines1, cloneLines2 in pairwiseAgreement(cloneSetListCC, cloneSetListDuplo):
        print("\t\t" + filePath + ": " + str(agreement) +
              " (" + str(cloneLines1) + ", " + str(cloneLines2) + ")")
    print("\tCPD vs Duplo:")
    for filePath, agreement, cloneLines1, cloneLines2 in pairwiseAgreement(cloneSetListCPD, cloneSetListDuplo):
        print("\t\t" + filePath + ": " + str(agreement) +
              " (" + str(cloneLines1) + ", " + str(cloneLines2) + ")")

    # Find the largest clone of each tool no other found
    printBiggestOutlier(cloneSetListCC, cloneSetListCPD,
                        cloneSetListDuplo, "CCFinder")
    printBiggestOutlier(cloneSetListCPD, cloneSetListCC,
                        cloneSetListDuplo, "CPD")
    printBiggestOutlier(cloneSetListDuplo, cloneSetListCC,
                        cloneSetListCPD, "Duplo")

    # Clone heat map for RAY.f90
    if mode == 1:
        pathRAY = pathPrefix + "RAY.f90"
    else:
        pathRAY = pathPrefix + "RAY.FOR"
    lineHeatmapCSV(cloneSetListCC, cloneSetListCPD,
                   cloneSetListDuplo, pathRAY)

    lineCloneCount1 = fileCountLineDetections(cloneSetListCC, pathRAY)
    lineCloneCount2 = fileCountLineDetections(cloneSetListCPD, pathRAY)
    lineCloneCount3 = fileCountLineDetections(cloneSetListDuplo, pathRAY)

    plt.rcParams["figure.figsize"] = (18, 13)
    plt.rcParams.update({'font.size': 28})
    plt.plot(lineCloneCount1, label="CCFinderSW")
    plt.plot(lineCloneCount2, label="CPD")
    plt.plot(lineCloneCount3, label="Duplo")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()

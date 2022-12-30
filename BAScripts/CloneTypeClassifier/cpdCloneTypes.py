import math
import string
from datetime import datetime
import re

# Function to extract the number of lines, number of clones and the starting
# line of the clones in each clone group.
# Returns three lists:
# numberOfLines: list of line count for each clone group
# numberOfClones: list of clone count for each clone group
# startLine: list of tuples (file path, line number) for each clone in each clone group
def extractClones(fileName: string):
    numberOfLines = []
    numberOfClones = []
    startLine = []
    with open(fileName, 'r') as f:
        lines = f.readlines()
        # Iterate over file and look for line starting with "Found a "
        
        for i in range(0, len(lines)-1):
            if lines[i].startswith("Found a "):
                line = lines[i].split()
                numberOfLines.append(int(line[2]))
                cloneCount = 0
                while lines[i+1].startswith("Starting at line "):
                    i += 1
                    cloneCount += 1
                    line = lines[i].split()
                    startLine.append([line[5], int(line[3])])
                
                numberOfClones.append(cloneCount)
                    
    return numberOfLines, numberOfClones, startLine

# Technically not a good approach since FORTRAN doesn't reserve words         
def isIdentifier(token: string):
    if token[0] not in string.ascii_letters:
        return False
    reservedWords = ["abstract", "allocatable", "allocate", "assign", "associate", "asynchronous", "backspace", "bind", "block", "block data", "call", "case", "class", "close", "codimension", "common", "contains", "contiguous", "continue", "critical", "cycle", "data", "deallocate", "deferred", "dimension", "do", "do concurrent", "elemental", "else", "else if", "elsewhere", "end", "endfile", "endif", "entry", "enum", "enumerator", "equivalence", "error stop", "exit", "extends", "external", "final", "flush", "forall", "format", "function", "generic", "goto", "if", "implicit", "import", "include", "inquire", "intent", "interface", "intrinsic", "lock", "module", "namelist", "non_overridable", "nopass", "nullify", "only", "open", "operator", "optional", "parameter", "pass", "pause", "pointer", "print", "private", "procedure", "program", "protected", "public", "pure", "read", "recursive", "result", "return", "rewind", "rewrite", "save", "select", "sequence", "stop", "submodule", "subroutine", "sync all", "sync images", "sync memory", "target", "then", "unlock", "use", "value", "volatile", "wait", "where", "while", "write"]
    if token in reservedWords:
        return False 
    return True
             
def removeComments(fragment: string):
    # Remove lines starting with '#' (preprocessor directives)
    fragment = re.sub('^#.*\n', '\n', fragment, flags=re.MULTILINE)
    # Remove comments beginning with characters c or C (needs to follow new line)
    fragment = re.sub('^c.*\n', '\n', fragment, flags=re.MULTILINE)
    fragment = re.sub('^C.*\n', '\n', fragment, flags=re.MULTILINE)
    # Remove comments beginning with character !
    fragment = re.sub('!.*\n', '\n', fragment, flags=re.MULTILINE)
    
    # Check if first line is a comment or preprocessor directive
    if fragment.startswith('#') or fragment.startswith('c') or fragment.startswith('C'):
        fragment = re.sub('^.*\n', '\n', fragment, count=1)
    
    return fragment
    
# --- Similarity functions ---
# type-1: exact clone ignoring whitespace, comments and preprocessor directives
# type-2: type-1 but also allowing differences in identifiers and literal values
# type-3: type-2 but a few lines can be added or removed TODO: how many lines?
# type-4: code fragments, which are semantically equivalent but not syntactically equivalent
def isCategory1(fragment1: string, fragment2: string):
    similarity = 0
    
    # Check how many tokens are the same
    if len(fragment1) == len(fragment2):
        for i in range(0, len(fragment1)):
            if fragment1[i] == fragment2[i]:
                similarity += 1
        # Check if similarity is 100%
        if similarity == len(fragment1):
            return True
    
    return False

def isCategory2(fragment1: string, fragment2: string):
    similarity = 0
    
    if len(fragment1) == len(fragment2):
        for i in range(0, len(fragment1)):
            if fragment1[i] == fragment2[i]:
                similarity += 1
            elif isIdentifier(fragment1[i]) and isIdentifier(fragment2[i]):
                similarity += 1
        # Check if similarity is 100%
        if similarity == len(fragment1):
            return True
    
    return False

def isCategory3(fragment1: string, fragment2: string):
    similarity = 0
    
    # Check if length is similiar (10% difference)
    if not math.isclose(len(fragment1), len(fragment2), rel_tol=0.1):
        return False
    
    # Check how many tokens are the same
    for token in fragment1:
        if token in fragment2:
            similarity += 1
        elif isIdentifier(token):
            similarity += 1
    
    # Check if similarity is at least 95%
    if similarity/len(fragment1) >= 0.95:
        return True
    
    return False

def isCategory4(fragment1: string, fragment2: string):
    return False


def getCategory(fragments: list):
    category = 0
    
    # TODO: this will only correctly for 2 clones in one group
    for i in range(0, len(fragments)-1):
        for j in range(i+1, len(fragments)):
            fragment1 = fragments[i]
            fragment2 = fragments[j]
            # Remove comments
            fragment1 = removeComments(fragment1)
            fragment2 = removeComments(fragment2)
            
            # Split to remove whitespace
            fragment1 = fragment1.split()
            fragment2 = fragment2.split()
            
            # make lowercase
            fragment1 = [x.lower() for x in fragment1]
            fragment2 = [x.lower() for x in fragment2]
            
            if isCategory1(fragment1, fragment2):
                category = 1
            elif isCategory2(fragment1, fragment2):
                category = 2
            elif isCategory3(fragment1, fragment2):
                category = 3
            elif isCategory4(fragment1, fragment2):
                category = 4
            else:
                category = 0
        
    return category
             
# Function that gets category for each clone group
# Returns list with entry for each clone group
def getCategories(fragments: list, cloneCounts: list):
    categories = []
    # Categorize fragments
    offset = 0
    for cloneCount in cloneCounts:
        categories.append(getCategory(fragments[offset:cloneCount]))
        offset += cloneCount
                        
    return categories
        

def main():
    numberOfLines, numberOfClones, startLine = extractClones("text.txt")
    
    fragments = []
    
    for numLines, numClones in zip(numberOfLines, numberOfClones):
        for i in range(0, numClones):
            fragment = ""
            with open(startLine[i][0], 'r') as f:
                lines = f.readlines()
                for j in range(startLine[i][1]-1, startLine[i][1]+numLines-1):
                    fragment += lines[j]
            fragments.append(fragment)
    
    categories = getCategories(fragments, numberOfClones)
    
    # Get current time
    now = datetime.now()
    timeStamp = now.strftime("_%d_%m_%Y-%H:%M")

    filename = "fragments" + str(timeStamp) + ".txt"
    groupIndex = 0
    for numLines, numClones in zip(numberOfLines, numberOfClones):
        fragIdx = 0
        for i in range(0, numClones):
            # Write code fragments to file
            with open(filename, 'a') as f:
                f.write(">>>> Found a " + str(numLines) + " line clone of category " 
                        + str(categories[groupIndex]) + " from group " + str(groupIndex) 
                        + " at line " + str(startLine[i][1]) + " in " + startLine[i][0] 
                        + "\n")
                f.write(fragments[fragIdx])
                fragIdx += 1
                f.write(">>>> End of clone\n")
        groupIndex += 1

if __name__ == '__main__':
    main()
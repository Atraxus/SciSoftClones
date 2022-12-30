import string
import os



# Count lines of code in file
def countLines(fileName: string):
    with open(fileName, 'r') as f:
        lines = f.readlines()
        count = 0
        for line in lines:
            count += 1
    return count


# Function to count lines of all .f90 and .FOR files in given directory
def countLinesDir(directory: string):
    count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".f90") or file.endswith(".f77"):
                count += countLines(os.path.join(root, file))
    return count

# Count how many lines of code are code clones
def countCloneLines(fileName: string):
    with open(fileName, 'r') as f:
        lines = f.readlines()
        count = 0
        # Iterate over file and look for line starting with "Found a "
        for i, line in enumerate(lines):
            if line.startswith("Found a "):
                line = line.split()
                mult = 0
                i += 1
                while lines[i].startswith("Starting at line "):
                    mult += 1
                    i += 1
                count += int(line[2]) * mult
    return count




def main():
    projectLines = countLinesDir("/home/maierjan/Documents/Work/RAY/src/raycore/")
    cloneLines = countCloneLines("text1.txt")
    print("Project lines: " + str(projectLines))
    print("Clone lines: " + str(cloneLines))


if __name__ == '__main__':
    main()
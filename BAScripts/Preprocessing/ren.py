import glob, os
import sys

if __name__ == '__main__':
    folder = sys.argv[1]
    print(folder)
    # Check if folder is a valid directory
    if os.path.isdir(folder):
        print("Given string is valid path. Renaming files...")
        for filename in glob.iglob(os.path.join(folder, '*.FOR')):
            print("Renaming file: " + filename + " to " + filename.replace(".FOR", ".f90"))
            os.rename(filename, filename[:-4] + '.f90')
        for filename in glob.iglob(os.path.join(folder, '*.for')):
            print("Renaming file: " + filename + " to " + filename.replace(".for", ".f90"))
            os.rename(filename, filename[:-4] + '.f90')
        for filename in glob.iglob(os.path.join(folder, '*.f')):
            print("Renaming file: " + filename + " to " + filename.replace(".f", ".f90"))
            os.rename(filename, filename[:-4] + '.f90')
        for filename in glob.iglob(os.path.join(folder, '*.f77')):
            print("Renaming file: " + filename + " to " + filename.replace(".f77", ".f90"))
            os.rename(filename, filename[:-4] + '.f90')
    else:
        print('ERROR: Not a valid directory')
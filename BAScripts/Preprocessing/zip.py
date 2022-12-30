# This script is used to clean the code base of a project supposed to be used with NiCad.
# It changes the line endings to Unix style and removes all empty lines.

import os
import sys
import zipfile


if __name__ == '__main__':
	folder = sys.argv[1]
	windowsLineEnding = b'\r\n'
	linuxLineEnding = b'\n'

	allFiles = []
	for root, dirs, files in os.walk(folder):
		for name in files:
			if name.endswith('.f90'):
				fullPath = os.path.join(root, name)
				if fullPath.find('migrations') == -1:
					allFiles.append(fullPath)

	with zipfile.ZipFile(folder + '.zip', 'w') as myzip:
		for filename in allFiles:
			myzip.write(filename)

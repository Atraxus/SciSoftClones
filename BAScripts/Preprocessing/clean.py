# This script is used to clean the code base of a project supposed to be used with NiCad.
# It changes the line endings to Unix style and removes all empty lines.

import os
import sys
import re

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
  
	for filename in allFiles:
		with open(filename, 'rb') as f:
			content = f.read()
			# Remove '!' comments
			content = re.sub(b'!.*\n', b'\n', content)
			# Remove lines starting with '#' (preprocessor directives)
			content = re.sub(b'^#.*\n', b'\n', content, flags=re.MULTILINE)
			# Remove c C comment lines (c C needs to be at start of line)
			content = re.sub(b'^[cC\*].*\n', b'\n', content, flags=re.MULTILINE)
			# content = re.sub(b'^C.*\n', b'\n', content, flags=re.MULTILINE)	
			# Remove empty lines
			content = re.sub(b'^\s*\n', b'\n', content, flags=re.MULTILINE)

		with open(filename, 'wb') as f:
			f.write(content)
    
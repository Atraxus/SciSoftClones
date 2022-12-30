import re

if __name__ == '__main__':
    binString = b'This is a test'
    binString = re.sub(b'This', b'That', binString)
    print(binString)    
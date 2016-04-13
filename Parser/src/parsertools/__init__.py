import sys
import getpass


buildfilepath = __file__.rsplit('/', maxsplit=1)[0] + '/build'

with open(buildfilepath, 'r+') as buildfile:
    buildno = int(buildfile.read().rstrip())
    if getpass.getuser() == 'jeroenbruijning':
        buildfile.seek(0)
        buildfile.write(str(buildno + 1))
 
__version__ = '0.2.1'


class ParsertoolsException(Exception):
    pass

class NoPrefixError(ParsertoolsException):
    pass

print('parsertools version {}, build {}'.format(__version__, buildno))


if sys.version_info < (3,3):
    raise ParsertoolsException('This parser only works with Python 3.3 or later (due to unicode handling and other issues)')
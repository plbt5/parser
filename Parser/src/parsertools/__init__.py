import sys

class SparqlParserException(Exception):
    pass

if sys.version_info < (3,3):
    raise SparqlParserException('This parser only works with Python 3.3 or later (due to unicode handling and other issues)')
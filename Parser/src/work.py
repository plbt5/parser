from parsertools.parsers.sparqlparser import SPARQLParser, parseQuery, SPARQLStruct
import rfc3987

# s = '''
# # Comment
# BASE <http://example/base#>
# # Comment
# PREFIX : <http://example/>
# # Comment
# LOAD <http://example.org/faraway>
# # Comment
# '''[1:-1]
# 
# # r = parseQuery(s)
# # print(r.dump())
# # 
# # s = '''
# # BASE <http://example/base#>
# # PREFIX : <http://example/>
# # LOAD <http://example.org/faraway>
# # '''[1:-1]
# 
# 
# r = parseQuery(s)
# print(r.dump())

s = 'http://example/base#'

from pprint import pprint
pprint(rfc3987.parse(s))
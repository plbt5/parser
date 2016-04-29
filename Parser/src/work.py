# from parsertools.parsers.sparqlparser import SPARQLParser, parseQuery, SPARQLStruct
import rfc3987
import lxml

print(dir(lxml))

print(lxml.__path__)
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
from pprint import pprint

base = 'http://test#'
 
pprint(rfc3987.parse(base))
rel = 'foo'
 
print(rfc3987.resolve(base, rel))
 
 
pprint(rfc3987.parse(rfc3987.resolve(base, rel)))
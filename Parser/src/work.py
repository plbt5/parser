from parsertools.parsers.sparqlparser import SPARQLParser, parseQuery
import rfc3987



s = 'BASE <work:22?> SELECT REDUCED $var1 ?var2 (("*Expression*") AS $var3) { SELECT * {} } GROUP BY ROUND ( "*Expression*") VALUES $S { <testiri>  }'

r = parseQuery(s)


# print(r.dump())
# s = 'BASE <prologue:22> PREFIX prologue: <prologue:33> LOAD <testIri> ; BASE <prologue:22> PREFIX prologue: <prologue:33>'
# parseQuery(s)

# import pprint
# pprint.pprint(rfc3987.parse('testIri'))
# # pprint.pprint(rfc3987.parse('work:22?'))
# # pprint.pprint(rfc3987.parse('pref:double'))
# pprint.pprint(rfc3987.parse('test$iri:dach][t-het-wel'))

from parsertools.parsers.sparqlparser import SPARQLParser, parseQuery,\
    SPARQLStruct
import rfc3987



# s = 'BASE <work:22?> BASE <play:33> PREFIX piep: <somerefiex> SELECT REDUCED $var1 ?var2 (("*Expression*") AS $var3) { SELECT * {} } GROUP BY ROUND ( "*Expression*") VALUES $S { <testiri>  }'
s = 'BASE <prologue:22/> PREFIX prologue1: <prologue:33> LOAD <testIri> ; BASE <prologue:44> PREFIX prologue2: <prologue:33>'
r = parseQuery(s)

print(isinstance(r, SPARQLStruct))
r._applyPrefixesAndBase(baseiri='http://test/')

print(r.dump())

for elt in r.searchElements():
    for e in [elt.__class__.__name__, elt, elt.getPrefixes(), elt.getBaseiri()]:
        print(e)
    print()

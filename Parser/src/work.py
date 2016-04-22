from parsertools.parsers.sparqlparser import SPARQLParser, parseQuery,\
    SPARQLStruct
import rfc3987



s = 'BASE <work:22?> BASE <play:33> PREFIX piep: <somerefiex> SELECT REDUCED $var1 ?var2 (("*Expression*") AS $var3) { SELECT * {} } GROUP BY ROUND ( "*Expression*") VALUES $S { <testiri>  }'

r = parseQuery(s)

print(isinstance(r, SPARQLStruct))
r.applyPrefixesAndBase()

print(r.dump())

for elt in r.searchElements():
    print(elt, elt.__class__.__name__, elt.getPrefixes(), elt.getBaseiri())

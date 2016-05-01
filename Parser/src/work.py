from parsertools.parsers.sparqlparser import SPARQLParser, parseQuery, SPARQLElement
import rfc3987

s = 'BASE <prologue:22/> PREFIX prologue1: <prologue:33> LOAD <t:testIri> ; BASE <prologue:44> BASE </exttra> PREFIX prologue2: <prologue:55>'

r = parseQuery(s, base='test:')

print(r.dump())

r_answer1 = ''
for elt in r.searchElements():
    for e in [elt.__class__.__name__, elt, sorted(elt.getPrefixes().items()), elt.getBaseiri()]:
        r_answer1 += str(e) + '\n'
    r_answer1 += '\n'
    
print(r_answer1)
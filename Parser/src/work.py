from pyparsing import *
from parsertools.parsers.sparqlparser import *


s = '''        
# query op ontoTemp1A
PREFIX    ontoA:    <http://ts.tno.nl/mediator/1.0/examples/ontoTemp1A#>
PREFIX    rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?p ?v
WHERE {
    ?p rdf:type ontoA:Patient .
    ?p ontoA:hasTemp ?v
    FILTER (?v > 37.0)
}
'''[1:-1]

r = parseQuery(s)
print(r.dump())

from parsertools.parsers.sparqlparser import parseQuery, parser

q = '''
PREFIX ns:     <http://ds.tno.nl/ontoA/>
PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
PREFIX xsd:    <http://www.w3.org/2001/XMLSchema>

SELECT ?p ?t WHERE 
    {
        ?p a foaf:Person .
        ?p ns:hasTemp ?t .
        ?p ns:hasAge ?a .
         ?t a ns:TempInC .
         FILTER ( (datatype(?t) = xsd:float) &&
                     ( ?t > 37.0 ) &&
                     ( ?a < 37.0 ) 
                 ).
    } 
'''

r = parseQuery(q)
print(r.dump())

prefixDecls = r.searchElements(element_type=parser.PrefixDecl)
for p in prefixDecls:
    ns, ln = str(p.namespace)[:-1], str(p.localname)
    print("namespace: {} = {}".format(ns, ln))

new_ns = '_ns1'
for p in prefixDecls:
    if str(p.namespace)[0:-1] == 'ns':
        print('updating {} with {}'.format(str(p.namespace),new_ns))
        p.namespace.updateWith(new_ns)

print('updated namespace:')
for p in prefixDecls:
    ns, ln = str(p.namespace)[:-1], str(p.localname)
    print("namespace: {} = {}".format(ns, ln))
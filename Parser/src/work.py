from sparqlparser.grammar import *

ns = {
      'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
      'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
      'xmlns': 'http://knowledgeweb.semanticweb.org/heterogeneity/alignment#',
      'base': 'http://oms.omwg.org/wine-vin/',
      'wine': 'http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#',
      'vin': 'http://ontology.deri.org/vin#',
      'edoal': 'http://ns.inria.org/edoal/1.0/#'
      }

q = '''
PREFIX ns:     <http://ds.tno.nl>
PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
PREFIX xsd:    <http://www.w3.org/2001/XMLSchema>

SELECT ?p ?t WHERE 
    {
        ?p a foaf:Person ;
        ns:hasTemp ?t .
        ?t rdf:value ?b .
         FILTER (  (?t > ?a ) &&
                    ?b > 37.0 && 
                  langMatches(lang(?p), "EN")
                 ).
    } 
'''

r = parseQuery(q)
print(r.dump())

# TASK: find pattern below a TriplesSameSubjectPath
pattern = "ns:hasTemp"

tbs = r.searchElements(label = None, element_type=TriplesBlock, value=None, labeledOnly=False)
if not tbs:
    raise NotImplementedError('TriplesBlock expected but not found!')
print("TripleBlocks: ", tbs)
for tb in tbs:
    SSubPaths = tb.searchElements(element_type=TriplesSameSubjectPath, labeledOnly=False)
    if not SSubPaths: raise NotImplementedError('TriplesSameSubjectPath expected but not found!')
    else: 
        for ssp in SSubPaths:
            print("getItems : ", ssp.getItems())
            print("getValues: ", ssp.getValues())
            print("getName  : ", ssp.getName())

        vots = ssp.searchElements(value=pattern, labeledOnly=False)


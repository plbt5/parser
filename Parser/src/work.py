from pyparsing import *
from parsertools.parsers.sparqlparser import *


        
        
if __name__ == '__main__':

    s = '''
PREFIX  dc: <http://purl.org/dc/elements/1.1/>
PREFIX  : <http://example.org/book/>

SELECT  $title
WHERE   { :book1  dc:title  $title }
'''[1:-1]
    
    r = parseQuery(s)
    print(r)
    r.expandIris()
    print(r)
#     r_answer1 = ''
#     for elt in r.searchElements():
#         for e in [elt.__class__.__name__, elt, sorted(elt.getPrefixes().items()), elt.getBaseiri()]:
#             r_answer1 += str(e) + '\n'
#         r_answer1 += '\n'
#     print(r_answer1)
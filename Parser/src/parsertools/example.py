'''
Created on 1 apr. 2016

@author: jeroenbruijning
'''

#
# Example program for the use of parsertools
#

# Running a SPARQL parser

from parsertools.parsers.sparqlparser import sparqlparser as parser
from parsertools.parsers.sparqlparser import stripComments, parseQuery

# Parsing a complete query

query = '''
ASK { 
    SELECT * {}
    } 
    GROUP BY ROUND ("*Expression*")
    HAVING <test:227>
    (DISTINCT "*Expression*", "*Expression*", "*Expression*" )
'''

result = parseQuery(query)

print(result.dump())

# parsing a string representing a production in the SPARQL Grammar

element = '"work"@en-bf'

result = parser.RDFLiteral(element)

print(result.dump())
'''
Created on 1 apr. 2016

@author: jeroenbruijning
'''

#
# Example program for the use of parsertools
#

# Running a SPARQL parser

from parsertools.parsers.sparqlparser import parseQuery

# Parsing a complete query
# For this, only the import parseQuery is needed

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

# parseQuery above is actually a convenience function. It does some preprocessing (such as stripping
# comments from the query) and some postprocessing (to perform additional checks on the query that are
# part of the SPARQL specification outside the EBNF grammar). In between the query string is parsed against 
# a top level production of the grammar.
# For this, an actual SPARQL parser object is used. It has attributes for every production in the grammar (except for
# the "whitespace" production which is not needed with pyparsing).
# Such an attribute can be used to parse a valid string for that production. This is the basic mode of parsing.

# As an example, below a string is parsed against the RDFLiteral production.
# For this, we need to import sparqlparser.

from parsertools.parsers.sparqlparser import parser

rdfliteral = '"work"@en-bf'

result = parser.RDFLiteral(rdfliteral)

print(result.dump())
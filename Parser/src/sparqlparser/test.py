import sys
from pyparsing import *
from sparqlparser.grammar import *
from sparqlparser.grammar import stripComments
from sparqlparser.grammar_functest import printResults

s = '"work"@en-bf'

r = RDFLiteral(s)

print(r.dump())

e = r.searchElements(label='langtag')


for i in e:
    print(i.dump())
    print(i.getParent().dump())
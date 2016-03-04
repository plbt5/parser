import sys
from pyparsing import *
from sparqlparser.grammar import *
from sparqlparser.grammar import stripComments
from sparqlparser.grammar_functest import printResults

s = "test / test / test"

p = separatedList(Word(alphas), delim='/')

r = p.parseString(s)

print(r)

print(type(r))

s = 'a ? / ^ ! ( ^ <testIri> | ^ <testIri> )'

r = PathSequence(s)

# r.render()
# 
# print(r.dump()) 

l = ['a ? / ^ ! ( ^ <testIri> | ^ <testIri> ) | a ? / ^ ! ( ^ <testIri> | ^ <testIri> )']
printResults(l, 'PathAlternative', dump=True)  
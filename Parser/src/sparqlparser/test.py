import sys
from pyparsing import *
from sparqlparser.grammar import *
from sparqlparser.grammar import stripComments
from sparqlparser.grammar_functest import printResults

# l = ['<test>', 'a', '^<test>', '^ a']
# printResults(l, 'PathOneInPropertySet', dump=True)    



# PathOneInPropertySet_list_p = punctuatedList(PathOneInPropertySet_p)
print()
r = PathOneInPropertySet('^<test>')
# print(r)
# r.dump(output=sys.stdout)
print(r.dump())# print(repr(r))
r.render()
print(repr(r))
assert r == eval(repr(r))
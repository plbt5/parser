'''
Created on 24 feb. 2016

@author: jeroenbruijning
'''

from pyparsing import *
from sparqlparser.grammar import *

# setup

s = "'work' ^^<work>"

r = RDFLiteral(s)
assert r.check()


# check copy 

rc = r.copy()
rc2 = rc
assert rc is rc2
assert rc2 == r
assert not rc is r
# rc.lexical_form = String("'work2'")
rc.lexical_form.updateWith("'work2'")
assert rc == rc2
assert not rc2 == r

p = r.copy()
q = p.copy()

# check __str__ functie

assert r.__str__() == "'work' ^^ <work>" 
 
# check init van ParseInfo (twee manieren) geeft hetzelfde resultaat
 
assert r == RDFLiteral_p.parseString(s)[0]
 
# check dot access (read)
 
assert r.lexical_form.__str__() == "'work'"
assert r.isBranch()
assert not r.isAtom()

# check dot access (write)
 
# p.lexical_form = STRING_LITERAL1("'work'")
p.lexical_form.updateWith("'work'")
assert p.lexical_form.__str__() == "'work'"
assert p.__str__() == "'work' ^^ <work>"
assert p.yieldsValidExpression()
assert p.check()
assert r == p
 
p.lexical_form.updateWith("'work2'")
assert p.lexical_form.__str__() == "'work2'"
assert p.__str__() == "'work2' ^^ <work>"
assert p.yieldsValidExpression()
assert p.check()
 
q.lexical_form.updateWith("'work'")
assert q.lexical_form.__str__() == "'work'"
assert q.__str__() == "'work' ^^ <work>"
assert q.yieldsValidExpression()
assert q.check()
assert r == q

s = '(DISTINCT "*Expression*",  "*Expression*",   "*Expression*" )'
p = ArgList_p.parseString(s)[0]
q = ArgList(s)
 
assert p == q
assert p.__str__() == q.__str__()
assert p.hasLabel('distinct')
# p.expression_list.updateWith('"*Expression*"')
assert p.yieldsValidExpression()

# check util.stripComments()

s1 = """
<check#22?> ( $var, ?var )
# bla
'sdfasf# sdfsfd' # comment
"""[1:-1].split('\n')

s2 = """
<check#22?> ( $var, ?var )

'sdfasf# sdfsfd'
"""[1:-1]

assert stripComments(s1) == s2

# check ParseInfo.searchElements()

s = '<check#22?> ( $var, ?var )'
  
r = PrimaryExpression(s)
assert r.iriOrFunction.iri == iri('<check#22?>')

found = r.searchElements()

assert len(found) == 30, len(found)
found = r.searchElements(labeledOnly=False)
assert len(found) == 30, len(found)
found = r.searchElements(labeledOnly=True)
assert len(found) == 4, len(found)
found = r.searchElements(value='<check#22?>')
assert len(found) == 2, len(found)
assert type(found[0]) == iri
assert found[0].getLabel() == 'iri'
assert found[0].__str__() == '<check#22?>'



# check ParseInfo.updateWith()

found[0].updateWith('<9xx9!>')

assert r.iriOrFunction.iri == iri('<9xx9!>')

found = r.searchElements(value='<check#22?>')
assert len(found) == 0

found = r.searchElements(element_type=ArgList)
assert len(found) == 1, len(found)
arglist = found[0]

assert(len(arglist.getChildren())) == 2
  

ancestors = arglist.getAncestors(r)
assert str(ancestors) == '[iriOrFunction("<9xx9!> ( $var , ?var )"), PrimaryExpression("<9xx9!> ( $var , ?var )")]'


# Test parseQuery

s = 'BASE <work:22?> SELECT REDUCED $var1 ?var2 (("*Expression*") AS $var3) { SELECT * {} } GROUP BY ROUND ( "*Expression*") VALUES $S { <testIri> <testIri> }'
parseQuery(s)

s = 'BASE <prologue:22> PREFIX prologue: <prologue:33> LOAD <testIri> ; BASE <prologue:22> PREFIX prologue: <prologue:33>'
parseQuery(s)

# check ParseInfo.__repr__ and ParseInfo.__str__

s = '<check#22?> ( $var, ?var )'
  
r = PrimaryExpression(s)

# print(r.dump())

branch = r.descend()
assert branch.isBranch()
assert len(branch.getChildren()) > 0
# print('branch:', type(branch))
a = branch
while len(a.getChildren()) > 0:
    a = a.getChildren()[0]
assert a.isAtom()

assert r == eval(repr(r))
assert str(r) == '<check#22?> ( $var , ?var )'

s = '(DISTINCT "*Expression*",  "*Expression*",   "*Expression*" )'

s_dump = '''
[ArgList] /( DISTINCT "*Expression*" , "*Expression*" , "*Expression*" )/
|  (
|  > distinct:
|  [DISTINCT_kw] /DISTINCT/
|  |  DISTINCT
|  > argument:
|  [Expression] /"*Expression*"/
|  |  [ConditionalOrExpression] /"*Expression*"/
|  |  |  [ConditionalAndExpression] /"*Expression*"/
|  |  |  |  [ValueLogical] /"*Expression*"/
|  |  |  |  |  [RelationalExpression] /"*Expression*"/
|  |  |  |  |  |  [NumericExpression] /"*Expression*"/
|  |  |  |  |  |  |  [AdditiveExpression] /"*Expression*"/
|  |  |  |  |  |  |  |  [MultiplicativeExpression] /"*Expression*"/
|  |  |  |  |  |  |  |  |  [UnaryExpression] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  [PrimaryExpression] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  |  [RDFLiteral] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  |  |  > lexical_form:
|  |  |  |  |  |  |  |  |  |  |  |  [String] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  |  |  |  [STRING_LITERAL2] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  |  |  |  |  "*Expression*"
|  ,
|  > argument:
|  [Expression] /"*Expression*"/
|  |  [ConditionalOrExpression] /"*Expression*"/
|  |  |  [ConditionalAndExpression] /"*Expression*"/
|  |  |  |  [ValueLogical] /"*Expression*"/
|  |  |  |  |  [RelationalExpression] /"*Expression*"/
|  |  |  |  |  |  [NumericExpression] /"*Expression*"/
|  |  |  |  |  |  |  [AdditiveExpression] /"*Expression*"/
|  |  |  |  |  |  |  |  [MultiplicativeExpression] /"*Expression*"/
|  |  |  |  |  |  |  |  |  [UnaryExpression] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  [PrimaryExpression] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  |  [RDFLiteral] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  |  |  > lexical_form:
|  |  |  |  |  |  |  |  |  |  |  |  [String] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  |  |  |  [STRING_LITERAL2] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  |  |  |  |  "*Expression*"
|  ,
|  > argument:
|  [Expression] /"*Expression*"/
|  |  [ConditionalOrExpression] /"*Expression*"/
|  |  |  [ConditionalAndExpression] /"*Expression*"/
|  |  |  |  [ValueLogical] /"*Expression*"/
|  |  |  |  |  [RelationalExpression] /"*Expression*"/
|  |  |  |  |  |  [NumericExpression] /"*Expression*"/
|  |  |  |  |  |  |  [AdditiveExpression] /"*Expression*"/
|  |  |  |  |  |  |  |  [MultiplicativeExpression] /"*Expression*"/
|  |  |  |  |  |  |  |  |  [UnaryExpression] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  [PrimaryExpression] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  |  [RDFLiteral] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  |  |  > lexical_form:
|  |  |  |  |  |  |  |  |  |  |  |  [String] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  |  |  |  [STRING_LITERAL2] /"*Expression*"/
|  |  |  |  |  |  |  |  |  |  |  |  |  |  "*Expression*"
|  )
'''[1:]

r = ArgList(s)


assert r.dump() == s_dump
assert r.descend() == r

v = r.searchElements(element_type=STRING_LITERAL2)
# print('STRING_LITERAL2 elements:', v)
assert v[0].isAtom()
assert not v[0].isBranch()

e = r.searchElements(element_type=Expression)[0]

# print(e, '\n', e.dump())

d = e.descend()

assert d.isAtom()



print('Passed')


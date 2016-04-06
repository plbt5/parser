'''
Created on 31 mrt. 2016

@author: jeroenbruijning
'''
from inspect import getmembers
from pyparsing import *
from parsertools.parsers.sparqlparser import parser
from parsertools.parsers.sparqlparser import stripComments, parseQuery

# basic parse
 
s = "'work' ^^<work>"
r = parser.RDFLiteral(s)
assert r.check()
  

# check copy 
  
rc = r.copy()
rc2 = rc
assert rc is rc2
assert rc2 == r
assert not rc is r

# test "dot" access label with copy
try:
    rc.lexical_form = parser.String("'work2'")
except AttributeError as e:
    assert str(e) == 'Direct setting of attributes not allowed. To change a labeled element, try updateWith() instead.', e
rc.lexical_form.updateWith("'work2'")
assert rc == rc2
assert not rc2 == r
  
p = r.copy()
q = p.copy()
  
# check __str__ functie
  
assert r.__str__() == "'work' ^^ <work>" 
 
   
# check dot access (read), and isBranch/isAtom methods
   
assert str(r.lexical_form) == "'work'"
assert r.isBranch()
assert not r.isAtom()
     
# test updateWith in combination with copy

p.lexical_form.updateWith("'work'")
assert str(p.lexical_form) == "'work'"
assert str(p) == "'work' ^^ <work>"
assert p.yieldsValidExpression()
assert p.check()
assert r == p
   
p.lexical_form.updateWith("'work2'")
assert str(p.lexical_form) == "'work2'"
assert str(p) == "'work2' ^^ <work>"
assert p.yieldsValidExpression()
assert p.check()
   
q.lexical_form.updateWith("'work'")
assert str(q.lexical_form) == "'work'"
assert str(q) == "'work' ^^ <work>"
assert q.yieldsValidExpression()
assert q.check()
assert r == q

s = '(DISTINCT "*Expression*",  "*Expression*",   "*Expression*" )'
p = parser.ArgList(s)

# test hasLabel

assert p.hasLabel('distinct')
assert p.yieldsValidExpression()
 
# check stripComments
 
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
 
s = '<check#22?> ( $var, ?var )'
   
r = parser.PrimaryExpression(s)

# test repeated dot access

assert r.iriOrFunction.iri == parser.iri('<check#22?>')

# check searchElements
 
found = r.searchElements()
assert len(found) == 32, len(found)

found = r.searchElements(labeledOnly=False)
assert len(found) == 32, len(found)

found = r.searchElements(labeledOnly=True)
assert len(found) == 4, len(found)

found = r.searchElements(value='<check#22?>')

assert len(found) == 2, len(found)
assert type(found[0]) == parser.iri
assert found[0].getLabel() == 'iri'
assert found[0].__str__() == '<check#22?>'
 
# check ParseInfo.updateWith()
 
found[0].updateWith('<9xx9!>')
 
assert r.iriOrFunction.iri == parser.iri('<9xx9!>')
 
found = r.searchElements(value='<check#22?>')
assert len(found) == 0
 
found = r.searchElements(element_type=parser.ArgList)
assert len(found) == 1, len(found)

# test getChilder, getAncestors

arglist = found[0]
assert(len(arglist.getChildren())) == 4, len(arglist.getChildren())
 
ancestors = arglist.getAncestors()
assert str(ancestors) == '[iriOrFunction("<9xx9!> ( $var , ?var )"), PrimaryExpression("<9xx9!> ( $var , ?var )")]'
 
# Test parseQuery
 
s = 'BASE <work:22?> SELECT REDUCED $var1 ?var2 (("*Expression*") AS $var3) { SELECT * {} } GROUP BY ROUND ( "*Expression*") VALUES $S { <testIri> <testIri> }'
parseQuery(s)
 
s = 'BASE <prologue:22> PREFIX prologue: <prologue:33> LOAD <testIri> ; BASE <prologue:22> PREFIX prologue: <prologue:33>'
r = parseQuery(s)
  
print(r.dump())

# test isAtom, isBranch
  
s = '<check#22?> ( $var, ?var )'
   
r = parser.PrimaryExpression(s)
   
branch = r.descend()
assert branch.isBranch()
assert len(branch.getChildren()) > 0
a = branch
while len(a.getChildren()) > 0:
    a = a.getChildren()[0]
assert a.isAtom()

# test str
 
assert r == eval('parser.' + repr(r))
assert str(r) == '<check#22?> ( $var , ?var )'

# test dump
 
s = '(DISTINCT "*Expression*",  "*Expression*",   "*Expression*" )'
 
s_dump = '''
[ArgList] /( DISTINCT "*Expression*" , "*Expression*" , "*Expression*" )/
|  [LPAR] /(/
|  |  (
|  > distinct:
|  [DISTINCT] /DISTINCT/
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
|  [RPAR] /)/
|  |  )
'''[1:]
 

r = parser.ArgList(s)

assert r.dump() == s_dump
assert r.descend() == r
 
# misc

v = r.searchElements(element_type=parser.STRING_LITERAL2)
assert v[0].isAtom()
assert not v[0].isBranch()
 
e = r.searchElements(element_type=parser.Expression)[0]
 
d = e.descend()
 
assert d.isAtom()
 
 
 
print('Passed')


'''
Created on 24 feb. 2016

@author: jeroenbruijning
'''

from pyparsing import *
from sparqlparser.grammar import *

# setup

s = "'work' ^^<work>"

r = RDFLiteral(s)
r.test()

# test copy 

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

# test __str__ functie

assert r.__str__() == "'work' ^^ <work>" 
 
# test init van ParseInfo (twee manieren) geeft hetzelfde resultaat
 
assert r == RDFLiteral_p.parseString(s)[0]
 
# test dot access (read)
 
assert r.lexical_form.__str__() == "'work'"

# test dot access (write)
 
# p.lexical_form = STRING_LITERAL1("'work'")
p.lexical_form.updateWith("'work'")
assert p.lexical_form.__str__() == "'work'"
assert p.__str__() == "'work' ^^ <work>"
assert p.yieldsValidExpression()
assert p.isValid()
assert r == p
 
p.lexical_form.updateWith("'work2'")
assert p.lexical_form.__str__() == "'work2'"
assert p.__str__() == "'work2' ^^ <work>"
assert p.yieldsValidExpression()
assert p.isValid()
 
q.lexical_form.updateWith("'work'")
assert q.lexical_form.__str__() == "'work'"
assert q.__str__() == "'work' ^^ <work>"
assert q.yieldsValidExpression()
assert q.isValid()
assert r == q

s = '(DISTINCT "*Expression*",  "*Expression*",   "*Expression*" )'
p = ArgList_p.parseString(s)[0]
q = ArgList(s)
 
assert p == q
assert p.__str__() == q.__str__()
assert p.hasLabel('distinct')
# p.expression_list.updateWith('"*Expression*"')
assert p.yieldsValidExpression()

# test util.stripComments()

s1 = """
<test#22?> ( $var, ?var )
# bla
'sdfasf# sdfsfd' # comment
"""[1:-1].split('\n')

s2 = """
<test#22?> ( $var, ?var )

'sdfasf# sdfsfd'
"""[1:-1]

assert stripComments(s1) == s2

# test ParseInfo.searchElements()

s = '<test#22?> ( $var, ?var )'
  
r = PrimaryExpression(s)

assert r.iriOrFunction.iri == iri('<test#22?>')

found = r.searchElements()
# assert len(found) == 3, len(found)

found = r.searchElements(labeledOnly=False)
# assert len(found) == 30, len(found)

found = r.searchElements(value='<test#22?>')
assert len(found) == 1
assert type(found[0]) == iri
assert found[0].getName() == 'iri'
assert found[0].__str__() == '<test#22?>'

# test ParseInfo.updateWith()

found[0].updateWith('<9xx9!>')

assert r.iriOrFunction.iri == iri('<9xx9!>')

found = r.searchElements(value='<test#22?>')
assert len(found) == 0

# Test parseQuery

s = 'BASE <work:22?> SELECT REDUCED $var1 ?var2 (("*Expression*") AS $var3) { SELECT * {} } GROUP BY ROUND ( "*Expression*") VALUES $S { <testIri> <testIri> }'
parseQuery(s)

s = 'BASE <prologue:22> PREFIX prologue: <prologue:33> LOAD <testIri> ; BASE <prologue:22> PREFIX prologue: <prologue:33>'
parseQuery(s)

# test ParseInfo.__repr__ and ParseInfo.__str__

s = '<test#22?> ( $var, ?var )'
  
r = PrimaryExpression(s)

assert r == eval(repr(r))
assert str(r) == '<test#22?> ( $var , ?var )'

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

print('Passed')


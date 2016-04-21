'''
Created on 20 apr. 2016

@author: jeroenbruijning
'''
import unittest

from parsertools.parsers.sparqlparser import SPARQLParser
from parsertools.parsers.sparqlparser import stripComments, parseQuery, unescapeUcode


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass

# ParseStruct tests

    def testParse(self):
        s = "'work' ^^<work>"
        r = SPARQLParser.RDFLiteral(s)
        assert r.check()
        
    def testCopy(self):
        s = "'work' ^^<work>"
        r = SPARQLParser.RDFLiteral(s)
        r_copy = r.copy()
        assert r_copy == r
        assert not r_copy is r
        
    def testStr(self):
        s = "'work' ^^<work>"
        r = SPARQLParser.RDFLiteral(s)
        assert r.__str__() == "'work' ^^ <work>" 

    def testLabelDotAccess(self):
        s = "'work' ^^<work>"
        r = SPARQLParser.RDFLiteral(s)
        assert str(r.lexical_form) == "'work'", r.lexical_form
        r_copy = r.copy()
        try:
            r_copy.lexical_form = SPARQLParser.String("'work2'")
        except AttributeError as e:
            assert str(e) == 'Direct setting of attributes not allowed. To change an element e, try e.updateWith() instead.'
            
        s = '<check#22?> ( $var, ?var )'
        r = SPARQLParser.PrimaryExpression(s)
        assert r.iriOrFunction.iri == SPARQLParser.iri('<check#22?>')
    
    def testUpdateWith(self):
        s = "'work' ^^<work>"
        r = SPARQLParser.RDFLiteral(s)
        r_copy = r.copy()
        r_copy.lexical_form.updateWith("'work2'")
        assert r_copy != r
        r_copy.lexical_form.updateWith("'work'")
        assert r_copy == r
        
    def testBranchAndAtom(self):
        s = "'work' ^^<work>"
        r = SPARQLParser.RDFLiteral(s)
        assert r.isBranch()
        assert not r.isAtom()
        assert (SPARQLParser.IRIREF('<ftp://test>')).isAtom()
        
    def testDescend(self):
        
        s = '(DISTINCT "*Expression*",  "*Expression*",   "*Expression*" )'
        r = SPARQLParser.ArgList(s)
        assert r.descend() == r        
        v = r.searchElements(element_type=SPARQLParser.STRING_LITERAL2)
        assert v[0].isAtom()
        assert not v[0].isBranch()
        e = r.searchElements(element_type=SPARQLParser.Expression)[0]
        d = e.descend()
        assert d.isAtom()
        
    def testStripComments(self):
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
    
    def testSearchElements(self):
        
        s = '<check#22?> ( $var, ?var )'
        r = SPARQLParser.PrimaryExpression(s)
        
        found = r.searchElements()
        assert len(found) == 32, len(found)
        
        found = r.searchElements(labeledOnly=False)
        assert len(found) == 32, len(found)
        
        found = r.searchElements(labeledOnly=True)
        assert len(found) == 4, len(found)
        
        found = r.searchElements(value='<check#22?>') 
        assert len(found) == 2, len(found)
        assert type(found[0]) == SPARQLParser.iri
        assert found[0].getLabel() == 'iri'
        assert found[0].__str__() == '<check#22?>'

    def testGetChildOrAncestors(self):
        s = '<check#22?> ( $var, ?var )'
        r = SPARQLParser.PrimaryExpression(s)
        found = r.searchElements(element_type=SPARQLParser.ArgList)
        arglist = found[0]
        assert(len(arglist.getChildren())) == 4, len(arglist.getChildren())
         
        ancestors = arglist.getAncestors()
        assert str(ancestors) == '[iriOrFunction("<check#22?> ( $var , ?var )"), PrimaryExpression("<check#22?> ( $var , ?var )")]'

    def testParseQuery(self):
        s = 'BASE <work:22?> SELECT REDUCED $var1 ?var2 (("*Expression*") AS $var3) { SELECT * {} } GROUP BY ROUND ( "*Expression*") VALUES $S { <testIri> <testIri> }'
        parseQuery(s)
        s = 'BASE <prologue:22> PREFIX prologue: <prologue:33> LOAD <testIri> ; BASE <prologue:22> PREFIX prologue: <prologue:33>'
        parseQuery(s)
    
    def testDump(self):
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
 
        r = SPARQLParser.ArgList(s)
        assert r.dump() == s_dump
        
    def testCheckIris(self):
        s = 'BASE <work:22?> SELECT REDUCED $var1 ?var2 (("*Expression*") AS $var3) { SELECT * {} } GROUP BY ROUND ( "*Expression*") VALUES $S { <test$iri:dach][t-het-wel> }'
        try:
            parseQuery(s)
            assert False
        except:
            assert True
        s = 'BASE <work:22?> SELECT REDUCED $var1 ?var2 (("*Expression*") AS $var3) { SELECT * {} } GROUP BY ROUND ( "*Expression*") VALUES $S { pref:testiri }'
        try:
            parseQuery(s)
            assert True
        except:
            assert False
            


# Other tests

    def testUnescapeUcode(self):
        s = 'abra\\U000C00AAcada\\u00AAbr\u99DDa'
        assert unescapeUcode(s) == 'abra󀂪cadaªbr駝a'

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
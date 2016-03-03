'''
Created on 24 feb. 2016

@author: jeroenbruijning
'''

from pyparsing import *
from sparqlparser import do_parseactions, SparqlParserException

# Parser for SPARQL 1.1, based on its EBNF syntax and using pyparsing.
# For the grammar see http://www.w3.org/TR/sparql11-query/#grammar.

# Auxiliary functions
#

def stripComments(text):
    '''Strips SPARQL-style comments from a multiline string'''
    if isinstance(text, list):
        text = '\n'.join(text)
    Comment = Literal('#') + SkipTo(lineEnd)
    NormalText = Regex('[^#<\'"]+')    
    Line = ZeroOrMore(String_p | IRIREF_p | NormalText) + Optional(Comment)
    Line.ignore(Comment)
    Line.setParseAction(lambda tokens: ' '.join([t if isinstance(t, str) else t.__str__() for t in tokens]))
    lines = text.split('\n')
    return '\n'.join([Line.parseString(l)[0] for l in lines])

def prepareQuery(querystring):
    '''Used to prepare a string for parsing. See the applicable comments and remarks in https://www.w3.org/TR/sparql11-query/, sections 19.1 - 19.8.'''
    # TODO: finish
    stripped = stripComments(querystring)
    return stripped

def checkQueryResult(r):
    '''Used to preform additional checks on the parse result. These are conditions that are not covered by the EBNF syntax.
    See the applicable comments and remarks in https://www.w3.org/TR/sparql11-query/, sections 19.1 - 19.8.'''
    #TODO: finish
    return True
#
# Main function to call
#

def parseQuery(querystring):
    s = prepareQuery(querystring)
    try:
        result = QueryUnit(s)
    except ParseException:
        try:
            result = UpdateUnit(s)
        except ParseException:
            raise SparqlParserException('Query {} cannot be parsed'.format(querystring))
    assert checkQueryResult(result), 'Fault in postprocessing query {}'.format(querystring)
    return result

#
# Base classes for representative objects
#

# do_parseactions = False

class ParsePattern(type):
    '''Metaclass for all ParseInfo classes.
    Sets "pattern" class attribute to the correct pyparsing pattern for the class.
    In the source, this pattern is consistently called <classname>_p.
    '''
    def __new__(cls, name, bases, namespace, **kwds):
        result = type.__new__(cls, name, bases, dict(namespace))
        try:
            result.pattern = eval(name+'_p')
        except NameError:
            result.pattern = None
        return result
    
class ParseInfo(metaclass=ParsePattern):
    '''Parent class for all ParseInfo subclasses. These subclasses form a hierarchy, the leaves of which
    correspond to productions in the SPARQL EBNF grammar (with one or two exceptions).
    '''
    def __init__(self, *args):
        '''A ParseInfo object can be initialized wih either a valid string for the subclass initialized,
        using its own pattern attribute to parse it, or it can be initialized with a name and a list of items
        which together form an existing and valid parse result. The latter option is only meant to be
        used by internal parser processes. The normal use case is to feed it with a string.
        Each item is a pair consisting of a name and either
        - a string
        - another ParseInfo object.
        Only in the latter case the name can be other than None.
        This nested list is the basic internal structure for the class and contains all parsing information.'''
        if len(args) == 2:
            self.__dict__['name'] = args[0] 
            self.__dict__['items'] = args[1] 
        else:
            assert len(args) == 1 and isinstance(args[0], str)
            self.__dict__['name'] = None
            self.__dict__['items'] = self.__getPattern().parseString(args[0], parseAll=True)[0].items
        assert self.__isLabelConsistent()
                
    def __eq__(self, other):
        '''Compares the items part of both classes for equality, recursively.
        This means that the labels are not taken into account. This is because
        the labels are a form of annotation, separate from the parse tree in terms of
        encountered production rules. Equality means that all productions are identical.'''
        return self.__class__ == other.__class__ and self.items == other.items
    
    def __getattr__(self, label):
        '''Retrieves the unique element corresponding to the label (non-recursive). Raises an exception if zero, or more than one values exist.'''
        if label in self.getLabels():
            values = self.getValuesForLabel(label)
            assert len(values) == 1
            return values[0] 
        else:
            raise AttributeError('Unknown label: {}'.format(label))
        
    def __setattr__(self, label, value):
        '''Raises exception when trying to set attributes directly.Elements are to be changed using "updateWith()".'''
        raise AttributeError('Direct setting of attributes not allowed. Try updateWith() instead.')
    
    def __repr__(self):
        return self.__class__.__name__ + '("' + str(self) + '")'
   
    def __isLabelConsistent(self):
        '''Checks if for labels are only not None for pairs [label, value] where value is a ParseInfo instance, and in those cases label must be equal to value.name.
        This is for internal use only.'''
        return all([i[0] == i[1].name if isinstance(i[1], ParseInfo) else i[0] == None if isinstance(i[1], str) else False for i in self.getItems()]) and \
                all([i[1].__isLabelConsistent() if isinstance(i[1], ParseInfo) else True for i in self.getItems()])

    def __getPattern(self):
        '''Returns the pattern used to parse expressions for this class.'''
        return self.__class__.pattern
        
    def __copyItems(self):
        '''Returns a deep copy of the items attribute. For internal use only.'''
        result = []
        for k, v in self.items:
            if isinstance(v, str):
                result.append([k, v])
            else:
                assert isinstance(v, ParseInfo)
                result.append([k, v.copy()])
        return result
    
    def __getElements(self, labeledOnly = True):
        '''For internal use. Returns a flat list of all pairs [label, value] value is a ParseInfo instance,
        at any depth of recursion.
        If labeledOnly is True, then in addition label may not be None.'''
        
        def flattenPair(p):
            result = []
            if isinstance(p[1], ParseInfo):
                result.extend(p[1].__getElements(labeledOnly=labeledOnly))
#             elif isinstance (p[1], list):
#                 result.extend(flattenList(p[1]))
            else:
                assert isinstance(p[1], str), type(p[1])
            return result
        
        def flattenList(l):
            result = []
            for p in l:
                result.extend(flattenPair(p))
            return result
        
        result = []
        if self.name or not labeledOnly:
                result.append(self)
        result.extend(flattenList(self.getItems()))
        return result  
    
    def searchElements(self, *, label=None, element_type = None, value = None, labeledOnly=True):
        '''Returns a list of all elements with the specified search pattern. If labeledOnly is True (the default case),
        only elements with label not None are considered for inclusion. Otherwise all elements are considered.
        Keyword arguments label, element_type, value are used as a wildcard if None. All must be matched for an element to be included in the result.'''
        
        result = []
        for e in self.__getElements(labeledOnly=labeledOnly):
            if label and label != e.getName():
                continue
            if element_type and element_type != e.__class__:
                continue
            if value and e != e.pattern.parseString(value)[0]:
                continue
            result.append(e)
        return result    
        
    def copy(self):
        '''Returns a deep copy of itself.'''
        result = globals()[self.__class__.__name__](self.name, self.__copyItems())
        assert result == self
        return result
    
    def updateWith(self, new_content):
        '''Replaces the items attribute with the items attribute of a freshly parsed new_content, which must be a string.
        The parsing is done with the pattern of the element being updated.
        This is the core function to change elements in place.'''
        assert isinstance(new_content, str), 'UpdateFrom function needs a string'
        try:
            other = self.pattern.parseString(new_content)[0]
        except ParseException:
            raise SparqlParserException('{} is not a valid string for {} element'.format(new_content, self.__class__.__name__))        
        self.__dict__['items'] = other.__dict__['items']
        assert self.isValid()
    
    def test(self, *, render=False, dump=False):
        '''Prints a report with the result of various checks. Optionally renders and/or dumps itself.'''
        print('{} is{}internally label-consistent'.format(self, ' ' if self.__isLabelConsistent() else ' not '))
        print('{} renders a{}expression ({})'.format(self, ' valid ' if self.yieldsValidExpression() else 'n invalid ', self.__str__()))
        print('{} is a{}valid parse object'.format(self, ' ' if self.isValid() else ' not '))
        if render:
            print('--rendering:')
            self.render()
        if dump:
            print('--dump:')
            self.dump()

    def getName(self):
        '''Returns name attribute (non-recursive).'''
        return self.name
    
    def getItems(self):
        '''Returns items attribute (non-recursive).'''
        return self.items
    
    def getValues(self):
        '''Returns list of all values from items attribute (non-recursive).'''
        return [i[1] for i in self.getItems()]
     
    def getLabels(self):
        '''Returns list of all labels from items attribute (non-recursive).'''
        return [i[0] for i in self.getItems() if i[0]]
    
    def hasLabel(self, k):
        '''True if k present as label (non-recursive).'''
        return k in self.getLabels()
    
    def getValuesForLabel(self, k):
        '''Returns list of all values for label. (Non-recursive).'''
        return [i[1] for i in self.getItems() if i[0] == k]
    
    def getItemsForLabel(self, k):
        '''Returns list of items with given label. (Non-recursive).'''
        return [i for i in self.getItems() if i[0] == k]

    def dump(self, indent='', step='|  '):
        '''Returns a dump of the object, with rich information'''
        result = ''
        def dumpString(s, indent, step):
            return indent + s + '\n'
        
        def dumpItems(items, indent, step):
            result = ''
            for _, v in items:
                if isinstance(v, str):
                    result += dumpString(v, indent+step, step)
#                 elif isinstance(v, list):
#                     dumpItems(v, indent+step, step)
                else:
                    assert isinstance(v, ParseInfo)
                    result += v.dump(indent+step, step)
            return result       
       
        result += indent + ('> '+ self.name + ':\n' + indent if self.name else '') + '[' + self.__class__.__name__ + '] ' + '/' + self.__str__() + '/' + '\n'
        result += dumpItems(self.items, indent, step)
        
        return result

    def __str__(self):
        '''Generates the string corresponding to the object. Except for whitespace variations, 
        this is identical to the string that was used to create the object.'''
        sep = ' '
#         def renderList(l):
#             resultList = []
#             for i in l:
#                 if isinstance(i, str):
#                     resultList.append(i)
#                     continue
#                 if isinstance(i, ParseInfo):
#                     resultList.append(i.__str__())
#                     continue
#                 if isinstance(i, list):
#                     resultList.append(renderList(i))
#             return sep.join(resultList)
        result = []
        for t in self.items:
            if isinstance(t[1], str):
                result.append(t[1]) 
#             elif isinstance(t[1], list):
#                 result.append(renderList(t[1]))
            else:
                assert isinstance(t[1], ParseInfo), type(t[1])
                result.append(t[1].__str__())
        return sep.join([r for r in result if r != ''])
    
    def render(self):
        print(self.__str__())
    
    def yieldsValidExpression(self):
        '''Returns True if the rendered expression can be parsed again to an element of the same class.
        This should normally be the case.'''
        try:
            self.__getPattern().parseString(self.__str__(), parseAll=True)
            return True
        except ParseException:
            return False
        
    def isValid(self):
        '''Returns True if the object is equal to the result of re-parsing its own rendering.
        This should normally be the case.'''
        return self.getItems() == self.__getPattern().parseString(self.__str__())[0].getItems()
    
    
def __parseInfoFunc(cls):
    '''Returns the function that converts a ParseResults object to a ParseInfo object of class "cls", with name set to None, and
    items set to a recursive list of [name, value] pairs (see below).
    The function returned is used to set a parseAction for a pattern.'''
            
    def labeledList(parseresults):
        '''For internal use. Converts a ParseResults object to a recursive structure consisting of a list of pairs [name, obj],
        where name is a label and obj either a string, a ParseInfo object, or again a similar list.'''
        while len(parseresults) == 1 and isinstance(parseresults[0], ParseResults):
            parseresults = parseresults[0]
        valuedict = dict((id(t), k) for (k, t) in parseresults.items())
        assert len(valuedict) == len(list(parseresults.items())), 'internal error: len(valuedict) = {}, len(parseresults.items) = {}'.format(len(valuedict), len(list(parseresults.items)))
        result = []
        for t in parseresults:
            if isinstance(t, str):
                result.append([None, t])
            elif isinstance(t, ParseInfo):
                t.__dict__['name'] = valuedict.get(id(t))
                result.append([valuedict.get(id(t)), t])
            elif isinstance(t, list):
                result.append(t)
            else:
                assert isinstance(t, ParseResults), type(t)
                assert valuedict.get(id(t)) == None, 'Error: found name ({}) for compound expression {}, remove'.format(valuedict.get(id(t)), t.__str__())
                result.extend(labeledList(t))
        return result
    
    def makeparseinfo(parseresults):
        '''The function to be returned.'''
        assert isinstance(cls, ParsePattern), type(cls)
        assert isinstance(parseresults, ParseResults)
        return cls(None, labeledList(parseresults))  
    
    return makeparseinfo

def punctuatedList(pattern, delim=','):
    '''Similar to a delimited list of instances from a ParseInfo subclass, but includes the delimiter in its ParseResults. Returns a 
    ParseResults object containing a simple list of matched tokens separated by the delimiter.'''
    
    def makeList(parseresults):
        assert len(parseresults) > 0, 'internal error'
        assert len(list((parseresults.keys()))) <= 1, 'internal error, got more than one key: {}'.format(list(parseresults.keys()))
        label = list(parseresults.keys())[0] if len(list(parseresults.keys())) == 1 else None
        assert all([p.__class__.pattern == pattern for p in parseresults if isinstance(p, ParseInfo)]), 'internal error: pattern mismatch ({}, {})'.format(p.__class__.pattern, pattern)
        templist = []
        for i in parseresults:
            if isinstance(i, ParseInfo):
                i.__dict__['name'] = label
                templist.append([label, i])
            else:
                assert isinstance(i, str)
                templist.append([None, i])
        result = []
        result.append(templist[0])
        for p in templist[1:]:
            result.append(delim)
            result.append(p)
        return result

    
    result = delimitedList(pattern, delim)
    if do_parseactions:
        result.setParseAction(makeList)
    return result

class SPARQLElement(ParseInfo):
    pass


class SPARQLNode(SPARQLElement):
    pass

            
class SPARQLTerminal(SPARQLNode):
    def __str__(self):
        return ''.join([t[1] for t in self.items])
            
            
class SPARQLNonTerminal(SPARQLNode):
    pass


class SPARQLKeyword(SPARQLElement):
    pass


class SPARQLOperator(SPARQLElement):
    pass



# Special tokens
ALL_VALUES_st_p = Literal('*')
class ALL_VALUES_st(SPARQLKeyword):
    pass
    def __str__(self):
        return '*'
if do_parseactions: ALL_VALUES_st_p.setName('ALL_VALUES_st').setParseAction(__parseInfoFunc((ALL_VALUES_st)))

#
# Brackets and interpunction
#

LPAR_p, RPAR_p, LBRACK_p, RBRACK_p, LCURL_p, RCURL_p, SEMICOL_p, COMMA_p, PERIOD_p = map(Literal, '()[]{};,.')

#
# Operators
#

NOT_op_p = Literal('!')
class NOT_op(SPARQLOperator):
    def __str__(self):
        return '!'
if do_parseactions: NOT_op_p.setName('NOT_op').setParseAction(__parseInfoFunc((NOT_op)))

PLUS_op_p = Literal('+')
class PLUS_op(SPARQLOperator):
    def __str__(self):
        return '+'
if do_parseactions: PLUS_op_p.setName('PLUS_op').setParseAction(__parseInfoFunc((PLUS_op)))

MINUS_op_p = Literal('-')
class MINUS_op(SPARQLOperator):
    def __str__(self):
        return '-'
if do_parseactions: MINUS_op_p.setName('MINUS_op').setParseAction(__parseInfoFunc((MINUS_op)))

TIMES_op_p = Literal('*')
class TIMES_op(SPARQLOperator):
    def __str__(self):
        return '*'
if do_parseactions: TIMES_op_p.setName('TIMES_op').setParseAction(__parseInfoFunc((TIMES_op)))

DIV_op_p = Literal('/')
class DIV_op(SPARQLOperator):
    def __str__(self):
        return '/'
if do_parseactions: DIV_op_p.setName('DIV_op').setParseAction(__parseInfoFunc((DIV_op)))

EQ_op_p = Literal('=') 
class EQ_op(SPARQLOperator):
    def __str__(self):
        return '='
if do_parseactions: EQ_op_p.setName('EQ_op').setParseAction(__parseInfoFunc((EQ_op)))

NE_op_p = Literal('!=') 
class NE_op(SPARQLOperator):
    def __str__(self):
        return '!='
if do_parseactions: NE_op_p.setName('NE_op').setParseAction(__parseInfoFunc((NE_op)))

GT_op_p = Literal('>') 
class GT_op(SPARQLOperator):
    def __str__(self):
        return '>'
if do_parseactions: GT_op_p.setName('GT_op').setParseAction(__parseInfoFunc((GT_op)))

LT_op_p = Literal('<') 
class LT_op(SPARQLOperator):
    def __str__(self):
        return '<'
if do_parseactions: LT_op_p.setName('LT_op').setParseAction(__parseInfoFunc((LT_op)))

GE_op_p = Literal('>=') 
class GE_op(SPARQLOperator):
    def __str__(self):
        return '>='
if do_parseactions: GE_op_p.setName('GE_op').setParseAction(__parseInfoFunc((GE_op)))

LE_op_p = Literal('<=') 
class LE_op(SPARQLOperator):
    def __str__(self):
        return '<='
if do_parseactions: LE_op_p.setName('LE_op').setParseAction(__parseInfoFunc((LE_op)))

AND_op_p = Literal('&&')
class AND_op(SPARQLOperator):
    def __str__(self):
        return '&&'
if do_parseactions: AND_op_p.setName('AND_op').setParseAction(__parseInfoFunc((AND_op)))
  
OR_op_p = Literal('||')
class OR_op(SPARQLOperator):
    def __str__(self):
        return '||'
if do_parseactions: OR_op_p.setName('OR_op').setParseAction(__parseInfoFunc((OR_op)))

INVERSE_op_p = Literal('^')
class INVERSE_op(SPARQLOperator):
    def __str__(self):
        return '^'
if do_parseactions: INVERSE_op_p.setName('INVERSE_op').setParseAction(__parseInfoFunc((INVERSE_op)))


#
# Keywords
#

TYPE_kw_p = Keyword('a')
class TYPE_kw(SPARQLKeyword):
    def __str__(self):
        return 'a'
if do_parseactions: TYPE_kw_p.setName('TYPE_kw').setParseAction(__parseInfoFunc((TYPE_kw)))

DISTINCT_kw_p = CaselessKeyword('DISTINCT')
class DISTINCT_kw(SPARQLKeyword):
    def __str__(self):
        return 'DISTINCT'
if do_parseactions: DISTINCT_kw_p.setName('DISTINCT_kw').setParseAction(__parseInfoFunc((DISTINCT_kw)))

COUNT_kw_p = CaselessKeyword('COUNT')
class COUNT_kw(SPARQLKeyword):
    def __str__(self):
        return 'COUNT'
if do_parseactions: COUNT_kw_p.setName('COUNT_kw').setParseAction(__parseInfoFunc((COUNT_kw)))

SUM_kw_p = CaselessKeyword('SUM')
class SUM_kw(SPARQLKeyword):
    def __str__(self):
        return 'SUM'
if do_parseactions: SUM_kw_p.setName('SUM_kw').setParseAction(__parseInfoFunc((SUM_kw)))

MIN_kw_p = CaselessKeyword('MIN') 
class MIN_kw(SPARQLKeyword):
    def __str__(self):
        return 'MIN'
if do_parseactions: MIN_kw_p.setName('MIN_kw').setParseAction(__parseInfoFunc((MIN_kw)))

MAX_kw_p = CaselessKeyword('MAX') 
class MAX_kw(SPARQLKeyword):
    def __str__(self):
        return 'MAX'
if do_parseactions: MAX_kw_p.setName('MAX_kw').setParseAction(__parseInfoFunc((MAX_kw)))

AVG_kw_p = CaselessKeyword('AVG') 
class AVG_kw(SPARQLKeyword):
    def __str__(self):
        return 'AVG'
if do_parseactions: AVG_kw_p.setName('AVG_kw').setParseAction(__parseInfoFunc((AVG_kw)))

SAMPLE_kw_p = CaselessKeyword('SAMPLE') 
class SAMPLE_kw(SPARQLKeyword):
    def __str__(self):
        return 'SAMPLE'
if do_parseactions: SAMPLE_kw_p.setName('SAMPLE_kw').setParseAction(__parseInfoFunc((SAMPLE_kw)))

GROUP_CONCAT_kw_p = CaselessKeyword('GROUP_CONCAT') 
class GROUP_CONCAT_kw(SPARQLKeyword):
    def __str__(self):
        return 'GROUP_CONCAT'
if do_parseactions: GROUP_CONCAT_kw_p.setName('GROUP_CONCAT_kw').setParseAction(__parseInfoFunc((GROUP_CONCAT_kw)))

SEPARATOR_kw_p = CaselessKeyword('SEPARATOR')
class SEPARATOR_kw(SPARQLKeyword):
    def __str__(self):
        return 'SEPARATOR'
if do_parseactions: SEPARATOR_kw_p.setName('SEPARATOR_kw').setParseAction(__parseInfoFunc((SEPARATOR_kw)))

NOT_kw_p = CaselessKeyword('NOT') + NotAny(CaselessKeyword('EXISTS') | CaselessKeyword('IN'))
class NOT_kw(SPARQLKeyword):
    def __str__(self):
        return 'NOT'
if do_parseactions: NOT_kw_p.setName('NOT_kw').setParseAction(__parseInfoFunc((NOT_kw)))

EXISTS_kw_p = CaselessKeyword('EXISTS')
class EXISTS_kw(SPARQLKeyword):
    def __str__(self):
        return 'EXISTS'
if do_parseactions: EXISTS_kw_p.setName('EXISTS_kw').setParseAction(__parseInfoFunc((EXISTS_kw)))

NOT_EXISTS_kw_p = CaselessKeyword('NOT') + CaselessKeyword('EXISTS')
class NOT_EXISTS_kw(SPARQLKeyword):
    def __str__(self):
        return 'NOT EXISTS'
if do_parseactions: NOT_EXISTS_kw_p.setName('NOT_EXISTS_kw').setParseAction(__parseInfoFunc((NOT_EXISTS_kw)))

REPLACE_kw_p = CaselessKeyword('REPLACE')
class REPLACE_kw(SPARQLKeyword):
    def __str__(self):
        return 'REPLACE'
if do_parseactions: REPLACE_kw_p.setName('REPLACE_kw').setParseAction(__parseInfoFunc((REPLACE_kw)))

SUBSTR_kw_p = CaselessKeyword('SUBSTR')
class SUBSTR_kw(SPARQLKeyword):
    def __str__(self):
        return 'SUBSTR'
if do_parseactions: SUBSTR_kw_p.setName('SUBSTR_kw').setParseAction(__parseInfoFunc((SUBSTR_kw)))

REGEX_kw_p = CaselessKeyword('REGEX')
class REGEX_kw(SPARQLKeyword):
    def __str__(self):
        return 'REGEX'
if do_parseactions: REGEX_kw_p.setName('REGEX_kw').setParseAction(__parseInfoFunc((REGEX_kw)))

STR_kw_p = CaselessKeyword('STR') 
class STR_kw(SPARQLKeyword):
    def __str__(self):
        return 'STR'
if do_parseactions: STR_kw_p.setName('STR_kw').setParseAction(__parseInfoFunc((STR_kw)))

LANG_kw_p = CaselessKeyword('LANG') 
class LANG_kw(SPARQLKeyword):
    def __str__(self):
        return 'LANG'
if do_parseactions: LANG_kw_p.setName('LANG_kw').setParseAction(__parseInfoFunc((LANG_kw)))

LANGMATCHES_kw_p = CaselessKeyword('LANGMATCHES') 
class LANGMATCHES_kw(SPARQLKeyword):
    def __str__(self):
        return 'LANGMATCHES'
if do_parseactions: LANGMATCHES_kw_p.setName('LANGMATCHES_kw').setParseAction(__parseInfoFunc((LANGMATCHES_kw)))

DATATYPE_kw_p = CaselessKeyword('DATATYPE') 
class DATATYPE_kw(SPARQLKeyword):
    def __str__(self):
        return 'DATATYPE'
if do_parseactions: DATATYPE_kw_p.setName('DATATYPE_kw').setParseAction(__parseInfoFunc((DATATYPE_kw)))

BOUND_kw_p = CaselessKeyword('BOUND') 
class BOUND_kw(SPARQLKeyword):
    def __str__(self):
        return 'BOUND'
if do_parseactions: BOUND_kw_p.setName('BOUND_kw').setParseAction(__parseInfoFunc((BOUND_kw)))

IRI_kw_p = CaselessKeyword('IRI') 
class IRI_kw(SPARQLKeyword):
    def __str__(self):
        return 'IRI'
if do_parseactions: IRI_kw_p.setName('IRI_kw').setParseAction(__parseInfoFunc((IRI_kw)))

URI_kw_p = CaselessKeyword('URI') 
class URI_kw(SPARQLKeyword):
    def __str__(self):
        return 'URI'
if do_parseactions: URI_kw_p.setName('URI_kw').setParseAction(__parseInfoFunc((URI_kw)))

BNODE_kw_p = CaselessKeyword('BNODE') 
class BNODE_kw(SPARQLKeyword):
    def __str__(self):
        return 'BNODE'
if do_parseactions: BNODE_kw_p.setName('BNODE_kw').setParseAction(__parseInfoFunc((BNODE_kw)))

RAND_kw_p = CaselessKeyword('RAND') 
class RAND_kw(SPARQLKeyword):
    def __str__(self):
        return 'RAND'
if do_parseactions: RAND_kw_p.setName('RAND_kw').setParseAction(__parseInfoFunc((RAND_kw)))

ABS_kw_p = CaselessKeyword('ABS') 
class ABS_kw(SPARQLKeyword):
    def __str__(self):
        return 'ABS'
if do_parseactions: ABS_kw_p.setName('ABS_kw').setParseAction(__parseInfoFunc((ABS_kw)))

CEIL_kw_p = CaselessKeyword('CEIL') 
class CEIL_kw(SPARQLKeyword):
    def __str__(self):
        return 'CEIL'
if do_parseactions: CEIL_kw_p.setName('CEIL_kw').setParseAction(__parseInfoFunc((CEIL_kw)))

FLOOR_kw_p = CaselessKeyword('FLOOR') 
class FLOOR_kw(SPARQLKeyword):
    def __str__(self):
        return 'FLOOR'
if do_parseactions: FLOOR_kw_p.setName('FLOOR_kw').setParseAction(__parseInfoFunc((FLOOR_kw)))

ROUND_kw_p = CaselessKeyword('ROUND') 
class ROUND_kw(SPARQLKeyword):
    def __str__(self):
        return 'ROUND'
if do_parseactions: ROUND_kw_p.setName('ROUND_kw').setParseAction(__parseInfoFunc((ROUND_kw)))

CONCAT_kw_p = CaselessKeyword('CONCAT') 
class CONCAT_kw(SPARQLKeyword):
    def __str__(self):
        return 'CONCAT'
if do_parseactions: CONCAT_kw_p.setName('CONCAT_kw').setParseAction(__parseInfoFunc((CONCAT_kw)))

STRLEN_kw_p = CaselessKeyword('STRLEN') 
class STRLEN_kw(SPARQLKeyword):
    def __str__(self):
        return 'STRLEN'
if do_parseactions: STRLEN_kw_p.setName('STRLEN_kw').setParseAction(__parseInfoFunc((STRLEN_kw)))

UCASE_kw_p = CaselessKeyword('UCASE') 
class UCASE_kw(SPARQLKeyword):
    def __str__(self):
        return 'UCASE'
if do_parseactions: UCASE_kw_p.setName('UCASE_kw').setParseAction(__parseInfoFunc((UCASE_kw)))

LCASE_kw_p = CaselessKeyword('LCASE') 
class LCASE_kw(SPARQLKeyword):
    def __str__(self):
        return 'LCASE'
if do_parseactions: LCASE_kw_p.setName('LCASE_kw').setParseAction(__parseInfoFunc((LCASE_kw)))

ENCODE_FOR_URI_kw_p = CaselessKeyword('ENCODE_FOR_URI') 
class ENCODE_FOR_URI_kw(SPARQLKeyword):
    def __str__(self):
        return 'ENCODE_FOR_URI'
if do_parseactions: ENCODE_FOR_URI_kw_p.setName('ENCODE_FOR_URI_kw').setParseAction(__parseInfoFunc((ENCODE_FOR_URI_kw)))

CONTAINS_kw_p = CaselessKeyword('CONTAINS') 
class CONTAINS_kw(SPARQLKeyword):
    def __str__(self):
        return 'CONTAINS'
if do_parseactions: CONTAINS_kw_p.setName('CONTAINS_kw').setParseAction(__parseInfoFunc((CONTAINS_kw)))

STRSTARTS_kw_p = CaselessKeyword('STRSTARTS') 
class STRSTARTS_kw(SPARQLKeyword):
    def __str__(self):
        return 'STRSTARTS'
if do_parseactions: STRSTARTS_kw_p.setName('STRSTARTS_kw').setParseAction(__parseInfoFunc((STRSTARTS_kw)))

STRENDS_kw_p = CaselessKeyword('STRENDS') 
class STRENDS_kw(SPARQLKeyword):
    def __str__(self):
        return 'STRENDS'
if do_parseactions: STRENDS_kw_p.setName('STRENDS_kw').setParseAction(__parseInfoFunc((STRENDS_kw)))

STRBEFORE_kw_p = CaselessKeyword('STRBEFORE') 
class STRBEFORE_kw(SPARQLKeyword):
    def __str__(self):
        return 'STRBEFORE'
if do_parseactions: STRBEFORE_kw_p.setName('STRBEFORE_kw').setParseAction(__parseInfoFunc((STRBEFORE_kw)))

STRAFTER_kw_p = CaselessKeyword('STRAFTER') 
class STRAFTER_kw(SPARQLKeyword):
    def __str__(self):
        return 'STRAFTER'
if do_parseactions: STRAFTER_kw_p.setName('STRAFTER_kw').setParseAction(__parseInfoFunc((STRAFTER_kw)))

YEAR_kw_p = CaselessKeyword('YEAR') 
class YEAR_kw(SPARQLKeyword):
    def __str__(self):
        return 'YEAR'
if do_parseactions: YEAR_kw_p.setName('YEAR_kw').setParseAction(__parseInfoFunc((YEAR_kw)))

MONTH_kw_p = CaselessKeyword('MONTH') 
class MONTH_kw(SPARQLKeyword):
    def __str__(self):
        return 'MONTH'
if do_parseactions: MONTH_kw_p.setName('MONTH_kw').setParseAction(__parseInfoFunc((MONTH_kw)))

DAY_kw_p = CaselessKeyword('DAY') 
class DAY_kw(SPARQLKeyword):
    def __str__(self):
        return 'DAY'
if do_parseactions: DAY_kw_p.setName('DAY_kw').setParseAction(__parseInfoFunc((DAY_kw)))

HOURS_kw_p = CaselessKeyword('HOURS') 
class HOURS_kw(SPARQLKeyword):
    def __str__(self):
        return 'HOURS'
if do_parseactions: HOURS_kw_p.setName('HOURS_kw').setParseAction(__parseInfoFunc((HOURS_kw)))

MINUTES_kw_p = CaselessKeyword('MINUTES') 
class MINUTES_kw(SPARQLKeyword):
    def __str__(self):
        return 'MINUTES'
if do_parseactions: MINUTES_kw_p.setName('MINUTES_kw').setParseAction(__parseInfoFunc((MINUTES_kw)))

SECONDS_kw_p = CaselessKeyword('SECONDS') 
class SECONDS_kw(SPARQLKeyword):
    def __str__(self):
        return 'SECONDS'
if do_parseactions: SECONDS_kw_p.setName('SECONDS_kw').setParseAction(__parseInfoFunc((SECONDS_kw)))

TIMEZONE_kw_p = CaselessKeyword('TIMEZONE') 
class TIMEZONE_kw(SPARQLKeyword):
    def __str__(self):
        return 'TIMEZONE'
if do_parseactions: TIMEZONE_kw_p.setName('TIMEZONE_kw').setParseAction(__parseInfoFunc((TIMEZONE_kw)))

TZ_kw_p = CaselessKeyword('TZ') 
class TZ_kw(SPARQLKeyword):
    def __str__(self):
        return 'TZ'
if do_parseactions: TZ_kw_p.setName('TZ_kw').setParseAction(__parseInfoFunc((TZ_kw)))

NOW_kw_p = CaselessKeyword('NOW') 
class NOW_kw(SPARQLKeyword):
    def __str__(self):
        return 'NOW'
if do_parseactions: NOW_kw_p.setName('NOW_kw').setParseAction(__parseInfoFunc((NOW_kw)))

UUID_kw_p = CaselessKeyword('UUID') 
class UUID_kw(SPARQLKeyword):
    def __str__(self):
        return 'UUID'
if do_parseactions: UUID_kw_p.setName('UUID_kw').setParseAction(__parseInfoFunc((UUID_kw)))

STRUUID_kw_p = CaselessKeyword('STRUUID') 
class STRUUID_kw(SPARQLKeyword):
    def __str__(self):
        return 'STRUUID'
if do_parseactions: STRUUID_kw_p.setName('STRUUID_kw').setParseAction(__parseInfoFunc((STRUUID_kw)))

MD5_kw_p = CaselessKeyword('MD5') 
class MD5_kw(SPARQLKeyword):
    def __str__(self):
        return 'MD5'
if do_parseactions: MD5_kw_p.setParseAction(__parseInfoFunc(MD5_kw))

SHA1_kw_p = CaselessKeyword('SHA1') 
class SHA1_kw(SPARQLKeyword):
    def __str__(self):
        return 'SHA1'
if do_parseactions: SHA1_kw_p.setParseAction(__parseInfoFunc(SHA1_kw))

SHA256_kw_p = CaselessKeyword('SHA256') 
class SHA256_kw(SPARQLKeyword):
    def __str__(self):
        return 'SHA256'
if do_parseactions: SHA256_kw_p.setParseAction(__parseInfoFunc(SHA256_kw))

SHA384_kw_p = CaselessKeyword('SHA384') 
class SHA384_kw(SPARQLKeyword):
    def __str__(self):
        return 'SHA384'
if do_parseactions: SHA384_kw_p.setParseAction(__parseInfoFunc(SHA384_kw))

SHA512_kw_p = CaselessKeyword('SHA512') 
class SHA512_kw(SPARQLKeyword):
    def __str__(self):
        return 'SHA512'
if do_parseactions: SHA512_kw_p.setParseAction(__parseInfoFunc(SHA512_kw))

COALESCE_kw_p = CaselessKeyword('COALESCE') 
class COALESCE_kw(SPARQLKeyword):
    def __str__(self):
        return 'COALESCE'
if do_parseactions: COALESCE_kw_p.setName('COALESCE_kw').setParseAction(__parseInfoFunc((COALESCE_kw)))

IF_kw_p = CaselessKeyword('IF') 
class IF_kw(SPARQLKeyword):
    def __str__(self):
        return 'IF'
if do_parseactions: IF_kw_p.setName('IF_kw').setParseAction(__parseInfoFunc((IF_kw)))

STRLANG_kw_p = CaselessKeyword('STRLANG') 
class STRLANG_kw(SPARQLKeyword):
    def __str__(self):
        return 'STRLANG'
if do_parseactions: STRLANG_kw_p.setName('STRLANG_kw').setParseAction(__parseInfoFunc((STRLANG_kw)))

STRDT_kw_p = CaselessKeyword('STRDT') 
class STRDT_kw(SPARQLKeyword):
    def __str__(self):
        return 'STRDT'
if do_parseactions: STRDT_kw_p.setName('STRDT_kw').setParseAction(__parseInfoFunc((STRDT_kw)))

sameTerm_kw_p = CaselessKeyword('sameTerm') 
class sameTerm_kw(SPARQLKeyword):
    def __str__(self):
        return 'sameTerm'
if do_parseactions: sameTerm_kw_p.setName('sameTerm_kw').setParseAction(__parseInfoFunc((sameTerm_kw)))

isIRI_kw_p = CaselessKeyword('isIRI') 
class isIRI_kw(SPARQLKeyword):
    def __str__(self):
        return 'isIRI'
if do_parseactions: isIRI_kw_p.setName('isIRI_kw').setParseAction(__parseInfoFunc((isIRI_kw)))

isURI_kw_p = CaselessKeyword('isURI') 
class isURI_kw(SPARQLKeyword):
    def __str__(self):
        return 'isURI'
if do_parseactions: isURI_kw_p.setName('isURI_kw').setParseAction(__parseInfoFunc((isURI_kw)))

isBLANK_kw_p = CaselessKeyword('isBLANK') 
class isBLANK_kw(SPARQLKeyword):
    def __str__(self):
        return 'isBLANK'
if do_parseactions: isBLANK_kw_p.setName('isBLANK_kw').setParseAction(__parseInfoFunc((isBLANK_kw)))

isLITERAL_kw_p = CaselessKeyword('isLITERAL') 
class isLITERAL_kw(SPARQLKeyword):
    def __str__(self):
        return 'isLITERAL'
if do_parseactions: isLITERAL_kw_p.setName('isLITERAL_kw').setParseAction(__parseInfoFunc((isLITERAL_kw)))

isNUMERIC_kw_p = CaselessKeyword('isNUMERIC') 
class isNUMERIC_kw(SPARQLKeyword):
    def __str__(self):
        return 'isNUMERIC'
if do_parseactions: isNUMERIC_kw_p.setName('isNUMERIC_kw').setParseAction(__parseInfoFunc((isNUMERIC_kw)))

IN_kw_p = CaselessKeyword('IN') 
class IN_kw(SPARQLKeyword):
    def __str__(self):
        return 'IN'
if do_parseactions: IN_kw_p.setName('IN_kw').setParseAction(__parseInfoFunc((IN_kw)))

NOT_IN_kw_p = CaselessKeyword('NOT') + CaselessKeyword('IN')
class NOT_IN_kw(SPARQLKeyword):
    def __str__(self):
        return 'NOT IN'
if do_parseactions: NOT_IN_kw_p.setName('NOT_IN_kw').setParseAction(__parseInfoFunc((NOT_IN_kw)))

FILTER_kw_p = CaselessKeyword('FILTER')
class FILTER_kw(SPARQLKeyword):
    def __str__(self):
        return 'FILTER'
if do_parseactions: FILTER_kw_p.setName('FILTER_kw').setParseAction(__parseInfoFunc((FILTER_kw)))

UNION_kw_p = CaselessKeyword('UNION')
class UNION_kw(SPARQLKeyword):
    def __str__(self):
        return 'UNION'
if do_parseactions: UNION_kw_p.setName('UNION_kw').setParseAction(__parseInfoFunc((UNION_kw)))

MINUS_kw_p = CaselessKeyword('MINUS')
class MINUS_kw(SPARQLKeyword):
    def __str__(self):
        return 'MINUS'
if do_parseactions: MINUS_kw_p.setName('MINUS_kw').setParseAction(__parseInfoFunc((MINUS_kw)))

UNDEF_kw_p = CaselessKeyword('UNDEF')
class UNDEF_kw(SPARQLKeyword):
    def __str__(self):
        return 'UNDEF'
if do_parseactions: UNDEF_kw_p.setName('UNDEF_kw').setParseAction(__parseInfoFunc((UNDEF_kw)))

VALUES_kw_p = CaselessKeyword('VALUES')
class VALUES_kw(SPARQLKeyword):
    def __str__(self):
        return 'VALUES'
if do_parseactions: VALUES_kw_p.setName('VALUES_kw').setParseAction(__parseInfoFunc((VALUES_kw)))

BIND_kw_p = CaselessKeyword('BIND')
class BIND_kw(SPARQLKeyword):
    def __str__(self):
        return 'BIND'
if do_parseactions: BIND_kw_p.setName('BIND_kw').setParseAction(__parseInfoFunc((BIND_kw)))

AS_kw_p = CaselessKeyword('AS')
class AS_kw(SPARQLKeyword):
    def __str__(self):
        return 'AS'
if do_parseactions: AS_kw_p.setName('AS_kw').setParseAction(__parseInfoFunc((AS_kw)))

SERVICE_kw_p = CaselessKeyword('SERVICE')
class SERVICE_kw(SPARQLKeyword):
    def __str__(self):
        return 'SERVICE'
if do_parseactions: SERVICE_kw_p.setName('SERVICE_kw').setParseAction(__parseInfoFunc((SERVICE_kw)))

SILENT_kw_p = CaselessKeyword('SILENT')
class SILENT_kw(SPARQLKeyword):
    def __str__(self):
        return 'SILENT'
if do_parseactions: SILENT_kw_p.setName('SILENT_kw').setParseAction(__parseInfoFunc((SILENT_kw)))

GRAPH_kw_p = CaselessKeyword('GRAPH')
class GRAPH_kw(SPARQLKeyword):
    def __str__(self):
        return 'GRAPH'
if do_parseactions: GRAPH_kw_p.setName('GRAPH_kw').setParseAction(__parseInfoFunc((GRAPH_kw)))

OPTIONAL_kw_p = CaselessKeyword('OPTIONAL')
class OPTIONAL_kw(SPARQLKeyword):
    def __str__(self):
        return 'OPTIONAL'
if do_parseactions: OPTIONAL_kw_p.setName('OPTIONAL_kw').setParseAction(__parseInfoFunc((OPTIONAL_kw)))

DEFAULT_kw_p = CaselessKeyword('DEFAULT')
class DEFAULT_kw(SPARQLKeyword):
    def __str__(self):
        return 'DEFAULT'
if do_parseactions: DEFAULT_kw_p.setName('DEFAULT_kw').setParseAction(__parseInfoFunc((DEFAULT_kw)))

NAMED_kw_p = CaselessKeyword('NAMED')
class NAMED_kw(SPARQLKeyword):
    def __str__(self):
        return 'NAMED'
if do_parseactions: NAMED_kw_p.setName('NAMED_kw').setParseAction(__parseInfoFunc((NAMED_kw)))

ALL_kw_p = CaselessKeyword('ALL')
class ALL_kw(SPARQLKeyword):
    def __str__(self):
        return 'ALL'
if do_parseactions: ALL_kw_p.setName('ALL_kw').setParseAction(__parseInfoFunc((ALL_kw)))

USING_kw_p = CaselessKeyword('USING')
class USING_kw(SPARQLKeyword):
    def __str__(self):
        return 'USING'
if do_parseactions: USING_kw_p.setName('USING_kw').setParseAction(__parseInfoFunc((USING_kw)))

INSERT_kw_p = CaselessKeyword('INSERT')
class INSERT_kw(SPARQLKeyword):
    def __str__(self):
        return 'INSERT'
if do_parseactions: INSERT_kw_p.setName('INSERT_kw').setParseAction(__parseInfoFunc((INSERT_kw)))

DELETE_kw_p = CaselessKeyword('DELETE')
class DELETE_kw(SPARQLKeyword):
    def __str__(self):
        return 'DELETE'
if do_parseactions: DELETE_kw_p.setName('DELETE_kw').setParseAction(__parseInfoFunc((DELETE_kw)))

WITH_kw_p = CaselessKeyword('WITH')
class WITH_kw(SPARQLKeyword):
    def __str__(self):
        return 'WITH'
if do_parseactions: WITH_kw_p.setName('WITH_kw').setParseAction(__parseInfoFunc((WITH_kw)))

WHERE_kw_p = CaselessKeyword('WHERE')
class WHERE_kw(SPARQLKeyword):
    def __str__(self):
        return 'WHERE'
if do_parseactions: WHERE_kw_p.setName('WHERE_kw').setParseAction(__parseInfoFunc((WHERE_kw)))

DELETE_WHERE_kw_p = CaselessKeyword('DELETE') + CaselessKeyword('WHERE')
class DELETE_WHERE_kw(SPARQLKeyword):
    def __str__(self):
        return 'DELETE WHERE'
if do_parseactions: DELETE_WHERE_kw_p.setName('DELETE_WHERE_kw').setParseAction(__parseInfoFunc((DELETE_WHERE_kw)))

DELETE_DATA_kw_p = CaselessKeyword('DELETE') + CaselessKeyword('DATA')
class DELETE_DATA_kw(SPARQLKeyword):
    def __str__(self):
        return 'DELETE DATA'
if do_parseactions: DELETE_DATA_kw_p.setName('DELETE_DATA_kw').setParseAction(__parseInfoFunc((DELETE_DATA_kw)))

INSERT_DATA_kw_p = CaselessKeyword('INSERT') + CaselessKeyword('DATA')
class INSERT_DATA_kw(SPARQLKeyword):
    def __str__(self):
        return 'INSERT DATA'
if do_parseactions: INSERT_DATA_kw_p.setName('INSERT_DATA_kw').setParseAction(__parseInfoFunc((INSERT_DATA_kw)))

COPY_kw_p = CaselessKeyword('COPY')
class COPY_kw(SPARQLKeyword):
    def __str__(self):
        return 'COPY'
if do_parseactions: COPY_kw_p.setName('COPY_kw').setParseAction(__parseInfoFunc((COPY_kw)))

MOVE_kw_p = CaselessKeyword('MOVE')
class MOVE_kw(SPARQLKeyword):
    def __str__(self):
        return 'MOVE'
if do_parseactions: MOVE_kw_p.setName('MOVE_kw').setParseAction(__parseInfoFunc((MOVE_kw)))

ADD_kw_p = CaselessKeyword('ADD')
class ADD_kw(SPARQLKeyword):
    def __str__(self):
        return 'ADD'
if do_parseactions: ADD_kw_p.setName('ADD_kw').setParseAction(__parseInfoFunc((ADD_kw)))

CREATE_kw_p = CaselessKeyword('CREATE')
class CREATE_kw(SPARQLKeyword):
    def __str__(self):
        return 'CREATE'
if do_parseactions: CREATE_kw_p.setName('CREATE_kw').setParseAction(__parseInfoFunc((CREATE_kw)))

DROP_kw_p = CaselessKeyword('DROP')
class DROP_kw(SPARQLKeyword):
    def __str__(self):
        return 'DROP'
if do_parseactions: DROP_kw_p.setName('DROP_kw').setParseAction(__parseInfoFunc((DROP_kw)))

CLEAR_kw_p = CaselessKeyword('CLEAR')
class CLEAR_kw(SPARQLKeyword):
    def __str__(self):
        return 'CLEAR'
if do_parseactions: CLEAR_kw_p.setName('CLEAR_kw').setParseAction(__parseInfoFunc((CLEAR_kw)))

LOAD_kw_p = CaselessKeyword('LOAD')
class LOAD_kw(SPARQLKeyword):
    def __str__(self):
        return 'LOAD'
if do_parseactions: LOAD_kw_p.setName('LOAD_kw').setParseAction(__parseInfoFunc((LOAD_kw)))

TO_kw_p = CaselessKeyword('TO')
class TO_kw(SPARQLKeyword):
    def __str__(self):
        return 'TO'
if do_parseactions: TO_kw_p.setName('TO_kw').setParseAction(__parseInfoFunc((TO_kw)))

INTO_kw_p = CaselessKeyword('INTO')
class INTO_kw(SPARQLKeyword):
    def __str__(self):
        return 'INTO'
if do_parseactions: INTO_kw_p.setName('INTO_kw').setParseAction(__parseInfoFunc((INTO_kw)))

OFFSET_kw_p = CaselessKeyword('OFFSET')
class OFFSET_kw(SPARQLKeyword):
    def __str__(self):
        return 'OFFSET'
if do_parseactions: OFFSET_kw_p.setName('OFFSET_kw').setParseAction(__parseInfoFunc((OFFSET_kw)))

LIMIT_kw_p = CaselessKeyword('LIMIT')
class LIMIT_kw(SPARQLKeyword):
    def __str__(self):
        return 'LIMIT'
if do_parseactions: LIMIT_kw_p.setName('LIMIT_kw').setParseAction(__parseInfoFunc((LIMIT_kw)))

ASC_kw_p = CaselessKeyword('ASC')
class ASC_kw(SPARQLKeyword):
    def __str__(self):
        return 'ASC'
if do_parseactions: ASC_kw_p.setName('ASC_kw').setParseAction(__parseInfoFunc((ASC_kw)))

DESC_kw_p = CaselessKeyword('DESC')
class DESC_kw(SPARQLKeyword):
    def __str__(self):
        return 'DESC'
if do_parseactions: DESC_kw_p.setName('DESC_kw').setParseAction(__parseInfoFunc((DESC_kw)))

ORDER_BY_kw_p = CaselessKeyword('ORDER') + CaselessKeyword('BY')
class ORDER_BY_kw(SPARQLKeyword):
    def __str__(self):
        return 'ORDER BY'
if do_parseactions: ORDER_BY_kw_p.setName('ORDER_BY_kw').setParseAction(__parseInfoFunc((ORDER_BY_kw)))

HAVING_kw_p = CaselessKeyword('HAVING') 
class HAVING_kw(SPARQLKeyword):
    def __str__(self):
        return 'HAVING'
if do_parseactions: HAVING_kw_p.setName('HAVING_kw').setParseAction(__parseInfoFunc((HAVING_kw)))

GROUP_BY_kw_p = CaselessKeyword('GROUP') + CaselessKeyword('BY') 
class GROUP_BY_kw(SPARQLKeyword):
    def __str__(self):
        return 'GROUP BY'
if do_parseactions: GROUP_BY_kw_p.setName('GROUP_BY_kw').setParseAction(__parseInfoFunc((GROUP_BY_kw)))

FROM_kw_p = CaselessKeyword('FROM')
class FROM_kw(SPARQLKeyword):
    def __str__(self):
        return 'FROM'
if do_parseactions: FROM_kw_p.setName('FROM_kw').setParseAction(__parseInfoFunc((FROM_kw)))

ASK_kw_p = CaselessKeyword('ASK')
class ASK_kw(SPARQLKeyword):
    def __str__(self):
        return 'ASK'
if do_parseactions: ASK_kw_p.setName('ASK_kw').setParseAction(__parseInfoFunc((ASK_kw)))

DESCRIBE_kw_p = CaselessKeyword('DESCRIBE')
class DESCRIBE_kw(SPARQLKeyword):
    def __str__(self):
        return 'DESCRIBE'
if do_parseactions: DESCRIBE_kw_p.setName('DESCRIBE_kw').setParseAction(__parseInfoFunc((DESCRIBE_kw)))

CONSTRUCT_kw_p = CaselessKeyword('CONSTRUCT')
class CONSTRUCT_kw(SPARQLKeyword):
    def __str__(self):
        return 'CONSTRUCT'
if do_parseactions: CONSTRUCT_kw_p.setName('CONSTRUCT_kw').setParseAction(__parseInfoFunc((CONSTRUCT_kw)))

SELECT_kw_p = CaselessKeyword('SELECT')
class SELECT_kw(SPARQLKeyword):
    def __str__(self):
        return 'SELECT'
if do_parseactions: SELECT_kw_p.setName('SELECT_kw').setParseAction(__parseInfoFunc((SELECT_kw)))

REDUCED_kw_p = CaselessKeyword('REDUCED')
class REDUCED_kw(SPARQLKeyword):
    def __str__(self):
        return 'REDUCED'
if do_parseactions: REDUCED_kw_p.setName('REDUCED_kw').setParseAction(__parseInfoFunc((REDUCED_kw)))

PREFIX_kw_p = CaselessKeyword('PREFIX')
class PREFIX_kw(SPARQLKeyword):
    def __str__(self):
        return 'PREFIX'
if do_parseactions: PREFIX_kw_p.setName('PREFIX_kw').setParseAction(__parseInfoFunc((PREFIX_kw)))

BASE_kw_p = CaselessKeyword('BASE')
class BASE_kw(SPARQLKeyword):
    def __str__(self):
        return 'BASE'
if do_parseactions: BASE_kw_p.setName('BASE_kw').setParseAction(__parseInfoFunc((BASE_kw)))


# 
# Parsers and classes for terminals
#

# [173]   PN_LOCAL_ESC      ::=   '\' ( '_' | '~' | '.' | '-' | '!' | '$' | '&' | "'" | '(' | ')' | '*' | '+' | ',' | ';' | '=' | '/' | '?' | '#' | '@' | '%' ) 
PN_LOCAL_ESC_e = r'\\[_~.\-!$&\'()*+,;=/?#@%]'
PN_LOCAL_ESC_p = Regex(PN_LOCAL_ESC_e)
class PN_LOCAL_ESC(SPARQLTerminal): pass
if do_parseactions: PN_LOCAL_ESC_p.setName('PN_LOCAL_ESC').setParseAction(__parseInfoFunc((PN_LOCAL_ESC)))


# [172]   HEX       ::=   [0-9] | [A-F] | [a-f] 
HEX_e = r'[0-9A-Fa-f]'
HEX_p = Regex(HEX_e)
class HEX(SPARQLTerminal): pass
if do_parseactions: HEX_p.setName('HEX').setParseAction(__parseInfoFunc((HEX)))

# [171]   PERCENT   ::=   '%' HEX HEX
PERCENT_e = r'%({})({})'.format( HEX_e, HEX_e)
PERCENT_p = Regex(PERCENT_e)
class PERCENT(SPARQLTerminal): pass
if do_parseactions: PERCENT_p.setName('PERCENT').setParseAction(__parseInfoFunc((PERCENT)))

# [170]   PLX       ::=   PERCENT | PN_LOCAL_ESC 
PLX_e = r'({})|({})'.format( PERCENT_e, PN_LOCAL_ESC_e)
PLX_p = Regex(PLX_e)
class PLX(SPARQLTerminal): pass
if do_parseactions: PLX_p.setName('PLX').setParseAction(__parseInfoFunc((PLX)))

# [164]   PN_CHARS_BASE     ::=   [A-Z] | [a-z] | [#x00C0-#x00D6] | [#x00D8-#x00F6] | [#x00F8-#x02FF] | [#x0370-#x037D] | [#x037F-#x1FFF] | [#x200C-#x200D] | [#x2070-#x218F] | [#x2C00-#x2FEF] | [#x3001-#xD7FF] | [#xF900-#xFDCF] | [#xFDF0-#xFFFD] | [#x10000-#xEFFFF] 
PN_CHARS_BASE_e = r'[A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\U00010000-\U000EFFFF]'
PN_CHARS_BASE_p = Regex(PN_CHARS_BASE_e)
class PN_CHARS_BASE(SPARQLTerminal): pass
if do_parseactions: PN_CHARS_BASE_p.setName('PN_CHARS_BASE').setParseAction(__parseInfoFunc((PN_CHARS_BASE)))

# [165]   PN_CHARS_U        ::=   PN_CHARS_BASE | '_' 
PN_CHARS_U_e = r'({})|({})'.format( PN_CHARS_BASE_e, r'_')
PN_CHARS_U_p = Regex(PN_CHARS_U_e)
class PN_CHARS_U(SPARQLTerminal): pass
if do_parseactions: PN_CHARS_U_p.setName('PN_CHARS_U').setParseAction(__parseInfoFunc((PN_CHARS_U)))

# [167]   PN_CHARS          ::=   PN_CHARS_U | '-' | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] 
PN_CHARS_e = r'({})|({})|({})|({})|({})|({})'.format( PN_CHARS_U_e, r'\-', r'[0-9]',  r'\u00B7', r'[\u0300-\u036F]', r'[\u203F-\u2040]')
PN_CHARS_p = Regex(PN_CHARS_e) 
class PN_CHARS(SPARQLTerminal): pass
if do_parseactions: PN_CHARS_p.setName('PN_CHARS').setParseAction(__parseInfoFunc((PN_CHARS)))

# [169]   PN_LOCAL          ::=   (PN_CHARS_U | ':' | [0-9] | PLX ) ((PN_CHARS | '.' | ':' | PLX)* (PN_CHARS | ':' | PLX) )?
PN_LOCAL_e = r'(({})|({})|({})|({}))((({})|({})|({})|({}))*(({})|({})|({})))?'.format( PN_CHARS_U_e, r':', r'[0-9]', PLX_e, PN_CHARS_e, r'\.', r':', PLX_e, PN_CHARS_e, r':', PLX_e) 
PN_LOCAL_p = Regex(PN_LOCAL_e)
class PN_LOCAL(SPARQLTerminal): pass
if do_parseactions: PN_LOCAL_p.setName('PN_LOCAL').setParseAction(__parseInfoFunc((PN_LOCAL)))
            
# [168]   PN_PREFIX         ::=   PN_CHARS_BASE ((PN_CHARS|'.')* PN_CHARS)?
PN_PREFIX_e = r'({})((({})|({}))*({}))?'.format( PN_CHARS_BASE_e, PN_CHARS_e, r'\.', PN_CHARS_e)
PN_PREFIX_p = Regex(PN_PREFIX_e)
class PN_PREFIX(SPARQLTerminal): pass
if do_parseactions: PN_PREFIX_p.setName('PN_PREFIX').setParseAction(__parseInfoFunc((PN_PREFIX)))

# [166]   VARNAME   ::=   ( PN_CHARS_U | [0-9] ) ( PN_CHARS_U | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] )* 
VARNAME_e = r'(({})|({}))(({})|({})|({})|({})|({}))*'.format( PN_CHARS_U_e, r'[0-9]', PN_CHARS_U_e, r'[0-9]', r'\u00B7', r'[\u0030-036F]', r'[\u0203-\u2040]')
VARNAME_p = Regex(VARNAME_e)
class VARNAME(SPARQLTerminal): pass
if do_parseactions: VARNAME_p.setName('VARNAME').setParseAction(__parseInfoFunc((VARNAME)))

# [163]   ANON      ::=   '[' WS* ']' 
ANON_p = Group(Literal('[') + Literal(']'))
class ANON(SPARQLTerminal): pass
if do_parseactions: ANON_p.setName('ANON').setParseAction(__parseInfoFunc((ANON)))

# [162]   WS        ::=   #x20 | #x9 | #xD | #xA 
# WS is not used
# In the SPARQL EBNF this production is used for defining NIL and ANON, but in this pyparsing implementation those are implemented differently

# [161]   NIL       ::=   '(' WS* ')' 
NIL_p = Group(Literal('(') + Literal(')'))
class NIL(SPARQLTerminal): pass
if do_parseactions: NIL_p.setName('NIL').setParseAction(__parseInfoFunc((NIL)))

# [160]   ECHAR     ::=   '\' [tbnrf\"']
ECHAR_e = r'\\[tbnrf\\"\']'
ECHAR_p = Regex(ECHAR_e) 
class ECHAR(SPARQLTerminal): pass
if do_parseactions: ECHAR_p.setName('ECHAR').setParseAction(__parseInfoFunc((ECHAR)))
 
# [159]   STRING_LITERAL_LONG2      ::=   '"""' ( ( '"' | '""' )? ( [^"\] | ECHAR ) )* '"""'  
STRING_LITERAL_LONG2_e = r'"""((""|")?(({})|({})))*"""'.format(r'[^"\\]', ECHAR_e)
STRING_LITERAL_LONG2_p = Regex(STRING_LITERAL_LONG2_e)
class STRING_LITERAL_LONG2(SPARQLTerminal):  
    pass
STRING_LITERAL_LONG2_p.parseWithTabs()
if do_parseactions: STRING_LITERAL_LONG2_p.setParseAction(__parseInfoFunc(STRING_LITERAL_LONG2))

# [158]   STRING_LITERAL_LONG1      ::=   "'''" ( ( "'" | "''" )? ( [^'\] | ECHAR ) )* "'''" 
STRING_LITERAL_LONG1_e = r"'''(('|'')?(({})|({})))*'''".format(r"[^'\\]", ECHAR_e)
STRING_LITERAL_LONG1_p = Regex(STRING_LITERAL_LONG1_e)  
class STRING_LITERAL_LONG1(SPARQLTerminal):  
    pass
STRING_LITERAL_LONG1_p.parseWithTabs()
if do_parseactions: STRING_LITERAL_LONG1_p.setParseAction(__parseInfoFunc(STRING_LITERAL_LONG1))

# [157]   STRING_LITERAL2   ::=   '"' ( ([^#x22#x5C#xA#xD]) | ECHAR )* '"' 
STRING_LITERAL2_e = r'"(({})|({}))*"'.format(ECHAR_e, r'[^\u0022\u005C\u000A\u000D]')
STRING_LITERAL2_p = Regex(STRING_LITERAL2_e)
class STRING_LITERAL2(SPARQLTerminal):  
    pass
STRING_LITERAL2_p.parseWithTabs()
if do_parseactions: STRING_LITERAL2_p.setParseAction(__parseInfoFunc(STRING_LITERAL2))
                           
# [156]   STRING_LITERAL1   ::=   "'" ( ([^#x27#x5C#xA#xD]) | ECHAR )* "'" 
STRING_LITERAL1_e = r"'(({})|({}))*'".format(ECHAR_e, r'[^\u0027\u005C\u000A\u000D]')
STRING_LITERAL1_p = Regex(STRING_LITERAL1_e)
class STRING_LITERAL1(SPARQLTerminal):  
    pass
STRING_LITERAL1_p.parseWithTabs()
if do_parseactions: STRING_LITERAL1_p.setParseAction(__parseInfoFunc(STRING_LITERAL1))
                            
# [155]   EXPONENT          ::=   [eE] [+-]? [0-9]+ 
EXPONENT_e = r'[eE][+-][0-9]+'
EXPONENT_p = Regex(EXPONENT_e)
class EXPONENT(SPARQLTerminal): pass
if do_parseactions: EXPONENT_p.setName('EXPONENT').setParseAction(__parseInfoFunc((EXPONENT)))

# [148]   DOUBLE    ::=   [0-9]+ '.' [0-9]* EXPONENT | '.' ([0-9])+ EXPONENT | ([0-9])+ EXPONENT 
DOUBLE_e = r'([0-9]+\.[0-9]*({}))|(\.[0-9]+({}))|([0-9]+({}))'.format(EXPONENT_e, EXPONENT_e, EXPONENT_e)
DOUBLE_p = Regex(DOUBLE_e)
class DOUBLE(SPARQLTerminal): pass
if do_parseactions: DOUBLE_p.setName('DOUBLE').setParseAction(__parseInfoFunc((DOUBLE)))

# [154]   DOUBLE_NEGATIVE   ::=   '-' DOUBLE 
DOUBLE_NEGATIVE_e = r'\-({})'.format(DOUBLE_e)
DOUBLE_NEGATIVE_p = Regex(DOUBLE_NEGATIVE_e)
class DOUBLE_NEGATIVE(SPARQLTerminal): pass
if do_parseactions: DOUBLE_NEGATIVE_p.setName('DOUBLE_NEGATIVE').setParseAction(__parseInfoFunc((DOUBLE_NEGATIVE)))

# [151]   DOUBLE_POSITIVE   ::=   '+' DOUBLE 
DOUBLE_POSITIVE_e = r'\+({})'.format(DOUBLE_e)
DOUBLE_POSITIVE_p = Regex(DOUBLE_POSITIVE_e)
class DOUBLE_POSITIVE(SPARQLTerminal): pass
if do_parseactions: DOUBLE_POSITIVE_p.setName('DOUBLE_POSITIVE').setParseAction(__parseInfoFunc((DOUBLE_POSITIVE)))

# [147]   DECIMAL   ::=   [0-9]* '.' [0-9]+ 
DECIMAL_e = r'[0-9]*\.[0-9]+'
DECIMAL_p = Regex(DECIMAL_e)
class DECIMAL(SPARQLTerminal): pass
if do_parseactions: DECIMAL_p.setName('DECIMAL').setParseAction(__parseInfoFunc((DECIMAL)))

# [153]   DECIMAL_NEGATIVE          ::=   '-' DECIMAL 
DECIMAL_NEGATIVE_e = r'\-({})'.format(DECIMAL_e)
DECIMAL_NEGATIVE_p = Regex(DECIMAL_NEGATIVE_e)
class DECIMAL_NEGATIVE(SPARQLTerminal): pass
if do_parseactions: DECIMAL_NEGATIVE_p.setName('DECIMAL_NEGATIVE').setParseAction(__parseInfoFunc((DECIMAL_NEGATIVE)))

# [150]   DECIMAL_POSITIVE          ::=   '+' DECIMAL 
DECIMAL_POSITIVE_e = r'\+({})'.format(DECIMAL_e)
DECIMAL_POSITIVE_p = Regex(DECIMAL_POSITIVE_e)
class DECIMAL_POSITIVE(SPARQLTerminal): pass
if do_parseactions: DECIMAL_POSITIVE_p.setName('DECIMAL_POSITIVE').setParseAction(__parseInfoFunc((DECIMAL_POSITIVE)))

# [146]   INTEGER   ::=   [0-9]+ 
INTEGER_e = r'[0-9]+'
INTEGER_p = Regex(INTEGER_e)
class INTEGER(SPARQLTerminal): pass
if do_parseactions: INTEGER_p.setName('INTEGER').setParseAction(__parseInfoFunc((INTEGER)))

# [152]   INTEGER_NEGATIVE          ::=   '-' INTEGER
INTEGER_NEGATIVE_e = r'\-({})'.format(INTEGER_e)
INTEGER_NEGATIVE_p = Regex(INTEGER_NEGATIVE_e)
class INTEGER_NEGATIVE(SPARQLTerminal): pass
if do_parseactions: INTEGER_NEGATIVE_p.setName('INTEGER_NEGATIVE').setParseAction(__parseInfoFunc((INTEGER_NEGATIVE)))

# [149]   INTEGER_POSITIVE          ::=   '+' INTEGER 
INTEGER_POSITIVE_e = r'\+({})'.format(INTEGER_e)
INTEGER_POSITIVE_p = Regex(INTEGER_POSITIVE_e)
class INTEGER_POSITIVE(SPARQLTerminal): pass
if do_parseactions: INTEGER_POSITIVE_p.setName('INTEGER_POSITIVE').setParseAction(__parseInfoFunc((INTEGER_POSITIVE)))

# [145]   LANGTAG   ::=   '@' [a-zA-Z]+ ('-' [a-zA-Z0-9]+)* 
LANGTAG_e = r'@[a-zA-Z]+(\-[a-zA-Z0-9]+)*'
LANGTAG_p = Regex(LANGTAG_e)
class LANGTAG(SPARQLTerminal): pass
if do_parseactions: LANGTAG_p.setName('LANGTAG').setParseAction(__parseInfoFunc((LANGTAG)))

# [144]   VAR2      ::=   '$' VARNAME 
VAR2_e = r'\$({})'.format(VARNAME_e)
VAR2_p = Regex(VAR2_e)
class VAR2(SPARQLTerminal): pass
if do_parseactions: VAR2_p.setParseAction(__parseInfoFunc(VAR2))

# [143]   VAR1      ::=   '?' VARNAME 
VAR1_e = r'\?({})'.format(VARNAME_e)
VAR1_p = Regex(VAR1_e)
class VAR1(SPARQLTerminal): pass
if do_parseactions: VAR1_p.setParseAction(__parseInfoFunc(VAR1))

# [142]   BLANK_NODE_LABEL          ::=   '_:' ( PN_CHARS_U | [0-9] ) ((PN_CHARS|'.')* PN_CHARS)?
BLANK_NODE_LABEL_e = r'_:(({})|[0-9])((({})|\.)*({}))?'.format(PN_CHARS_U_e, PN_CHARS_e, PN_CHARS_e)
BLANK_NODE_LABEL_p = Regex(BLANK_NODE_LABEL_e)
class BLANK_NODE_LABEL(SPARQLTerminal): pass
if do_parseactions: BLANK_NODE_LABEL_p.setName('BLANK_NODE_LABEL').setParseAction(__parseInfoFunc((BLANK_NODE_LABEL)))

# [140]   PNAME_NS          ::=   PN_PREFIX? ':'
PNAME_NS_e = r'({})?:'.format(PN_PREFIX_e)
PNAME_NS_p = Regex(PNAME_NS_e)
class PNAME_NS(SPARQLTerminal): pass
if do_parseactions: PNAME_NS_p.setName('PNAME_NS').setParseAction(__parseInfoFunc((PNAME_NS)))

# [141]   PNAME_LN          ::=   PNAME_NS PN_LOCAL 
PNAME_LN_e = r'({})({})'.format(PNAME_NS_e, PN_LOCAL_e)
PNAME_LN_p = Regex(PNAME_LN_e)
class PNAME_LN(SPARQLTerminal): pass
if do_parseactions: PNAME_LN_p.setName('PNAME_LN').setParseAction(__parseInfoFunc((PNAME_LN)))

# [139]   IRIREF    ::=   '<' ([^<>"{}|^`\]-[#x00-#x20])* '>' 
IRIREF_e = r'<[^<>"{}|^`\\\\\u0000-\u0020]*>'
IRIREF_p = Regex(IRIREF_e)
class IRIREF(SPARQLTerminal): pass
if do_parseactions: IRIREF_p.setName('IRIREF').setParseAction(__parseInfoFunc((IRIREF)))

#
# Parsers and classes for non-terminals
#

# [138]   BlankNode         ::=   BLANK_NODE_LABEL | ANON 
BlankNode_p = Group(BLANK_NODE_LABEL_p | ANON_p)
class BlankNode(SPARQLNonTerminal): pass
if do_parseactions: BlankNode_p.setName('BlankNode').setParseAction(__parseInfoFunc((BlankNode)))

# [137]   PrefixedName      ::=   PNAME_LN | PNAME_NS 
PrefixedName_p = Group(PNAME_LN_p ^ PNAME_NS_p)
class PrefixedName(SPARQLNonTerminal): pass
if do_parseactions: PrefixedName_p.setName('PrefixedName').setParseAction(__parseInfoFunc((PrefixedName)))

# [136]   iri       ::=   IRIREF | PrefixedName 
iri_p = Group(Group(IRIREF_p ^ PrefixedName_p))
class iri(SPARQLNonTerminal): pass
if do_parseactions: iri_p.setName('iri').setParseAction(__parseInfoFunc((iri)))

# [135]   String    ::=   STRING_LITERAL1 | STRING_LITERAL2 | STRING_LITERAL_LONG1 | STRING_LITERAL_LONG2 
String_p = Group(STRING_LITERAL1_p ^ STRING_LITERAL2_p ^ STRING_LITERAL_LONG1_p ^ STRING_LITERAL_LONG2_p)
class String(SPARQLNonTerminal):  
    pass
String_p.parseWithTabs()
if do_parseactions: String_p.setName('String').setParseAction(__parseInfoFunc((String)))
 
# [134]   BooleanLiteral    ::=   'true' | 'false' 
BooleanLiteral_p = Group(Literal('true') | Literal('false'))
class BooleanLiteral(SPARQLNonTerminal): pass
if do_parseactions: BooleanLiteral_p.setName('BooleanLiteral').setParseAction(__parseInfoFunc((BooleanLiteral)))
 
# # [133]   NumericLiteralNegative    ::=   INTEGER_NEGATIVE | DECIMAL_NEGATIVE | DOUBLE_NEGATIVE 
NumericLiteralNegative_p = Group(INTEGER_NEGATIVE_p ^ DECIMAL_NEGATIVE_p ^ DOUBLE_NEGATIVE_p)
class NumericLiteralNegative(SPARQLNonTerminal): pass
if do_parseactions: NumericLiteralNegative_p.setName('NumericLiteralNegative').setParseAction(__parseInfoFunc((NumericLiteralNegative)))
 
# # [132]   NumericLiteralPositive    ::=   INTEGER_POSITIVE | DECIMAL_POSITIVE | DOUBLE_POSITIVE 
NumericLiteralPositive_p = Group(INTEGER_POSITIVE_p ^ DECIMAL_POSITIVE_p ^ DOUBLE_POSITIVE_p)
class NumericLiteralPositive(SPARQLNonTerminal): pass
if do_parseactions: NumericLiteralPositive_p.setName('NumericLiteralPositive').setParseAction(__parseInfoFunc((NumericLiteralPositive)))
 
# # [131]   NumericLiteralUnsigned    ::=   INTEGER | DECIMAL | DOUBLE 
NumericLiteralUnsigned_p = Group(INTEGER_p ^ DECIMAL_p ^ DOUBLE_p)
class NumericLiteralUnsigned(SPARQLNonTerminal): pass
if do_parseactions: NumericLiteralUnsigned_p.setName('NumericLiteralUnsigned').setParseAction(__parseInfoFunc((NumericLiteralUnsigned)))
# 
# # [130]   NumericLiteral    ::=   NumericLiteralUnsigned | NumericLiteralPositive | NumericLiteralNegative 
NumericLiteral_p = Group(NumericLiteralUnsigned_p | NumericLiteralPositive_p | NumericLiteralNegative_p)
class NumericLiteral(SPARQLNonTerminal): pass
if do_parseactions: NumericLiteral_p.setName('NumericLiteral').setParseAction(__parseInfoFunc((NumericLiteral)))

# [129]   RDFLiteral        ::=   String ( LANGTAG | ( '^^' iri ) )? 
RDFLiteral_p = Group(String_p('lexical_form') + Optional(Group ((LANGTAG_p('langtag') ^ ('^^' + iri_p('datatype_uri'))))))
class RDFLiteral(SPARQLNonTerminal): pass
if do_parseactions: RDFLiteral_p.setName('RDFLiteral').setParseAction(__parseInfoFunc((RDFLiteral)))

Expression_p = Forward()
class Expression(SPARQLNonTerminal): pass
if do_parseactions: Expression_p.setName('Expression').setParseAction(__parseInfoFunc((Expression)))

# pattern and class to parse and __str__ delimited Expression lists
Expression_list_p = punctuatedList(Expression_p)
 
# [71]    ArgList   ::=   NIL | '(' 'DISTINCT'? Expression ( ',' Expression )* ')' 
ArgList_p = Group(NIL_p('nil')) | (LPAR_p + Optional(DISTINCT_kw_p('distinct')) + Expression_list_p('argument') + RPAR_p)
class ArgList(SPARQLNonTerminal): pass
if do_parseactions: ArgList_p.setName('ArgList').setParseAction(__parseInfoFunc((ArgList)))


# [128]   iriOrFunction     ::=   iri ArgList? 
iriOrFunction_p = Group(iri_p('iri') + Optional(Group(ArgList_p))('ArgList'))
class iriOrFunction(SPARQLNonTerminal): pass
if do_parseactions: iriOrFunction_p.setName('iriOrFunction').setParseAction(__parseInfoFunc((iriOrFunction)))

# [127]   Aggregate         ::=     'COUNT' '(' 'DISTINCT'? ( '*' | Expression ) ')' 
#             | 'SUM' '(' 'DISTINCT'? Expression ')' 
#             | 'MIN' '(' 'DISTINCT'? Expression ')' 
#             | 'MAX' '(' 'DISTINCT'? Expression ')' 
#             | 'AVG' '(' 'DISTINCT'? Expression ')' 
#             | 'SAMPLE' '(' 'DISTINCT'? Expression ')' 
#             | 'GROUP_CONCAT' '(' 'DISTINCT'? Expression ( ';' 'SEPARATOR' '=' String )? ')' 
Aggregate_p = Group(COUNT_kw_p('count') + LPAR_p + Optional(DISTINCT_kw_p('distinct')) + ( ALL_VALUES_st_p('all') ^ Expression_p('expression') ) + RPAR_p ) | \
            ( SUM_kw_p('sum') + LPAR_p + Optional(DISTINCT_kw_p('distinct')) + ( ALL_VALUES_st_p('all') ^ Expression_p('expression') ) + RPAR_p ) | \
            ( MIN_kw_p('min') + LPAR_p + Optional(DISTINCT_kw_p('distinct')) + ( ALL_VALUES_st_p('all') ^ Expression_p('expression') ) + RPAR_p ) | \
            ( MAX_kw_p('max') + LPAR_p + Optional(DISTINCT_kw_p('distinct')) + ( ALL_VALUES_st_p('all') ^ Expression_p('expression') ) + RPAR_p ) | \
            ( AVG_kw_p('avg') + LPAR_p + Optional(DISTINCT_kw_p('distinct')) + ( ALL_VALUES_st_p('all') ^ Expression_p('expression') ) + RPAR_p ) | \
            ( SAMPLE_kw_p('sample') + LPAR_p + Optional(DISTINCT_kw_p('distinct')) + ( ALL_VALUES_st_p('all') ^ Expression_p('expression') ) + RPAR_p ) | \
            ( GROUP_CONCAT_kw_p('group_concat') + LPAR_p + Optional(DISTINCT_kw_p('distinct')) + Expression_p('expression') + Optional( SEMICOL_p + SEPARATOR_kw_p + '=' + String_p('separator') ) + RPAR_p )
class Aggregate(SPARQLNonTerminal): pass
if do_parseactions: Aggregate_p.setName('Aggregate').setParseAction(__parseInfoFunc((Aggregate)))

GroupGraphPattern_p = Forward()
class GroupGraphPattern(SPARQLNonTerminal): pass
if do_parseactions: GroupGraphPattern_p.setName('GroupGraphPattern').setParseAction(__parseInfoFunc((GroupGraphPattern)))
 
# [126]   NotExistsFunc     ::=   'NOT' 'EXISTS' GroupGraphPattern 
NotExistsFunc_p = Group(NOT_EXISTS_kw_p + GroupGraphPattern_p('groupgraph'))
class NotExistsFunc(SPARQLNonTerminal): pass
if do_parseactions: NotExistsFunc_p.setName('NotExistsFunc').setParseAction(__parseInfoFunc((NotExistsFunc)))
 
# [125]   ExistsFunc        ::=   'EXISTS' GroupGraphPattern 
ExistsFunc_p = Group(EXISTS_kw_p + GroupGraphPattern_p('groupgraph'))
class ExistsFunc(SPARQLNonTerminal): pass
if do_parseactions: ExistsFunc_p.setName('ExistsFunc').setParseAction(__parseInfoFunc((ExistsFunc)))
 
# [124]   StrReplaceExpression      ::=   'REPLACE' '(' Expression ',' Expression ',' Expression ( ',' Expression )? ')' 
StrReplaceExpression_p = Group(REPLACE_kw_p + LPAR_p + Expression_p('arg') + COMMA_p + Expression_p('pattern') + COMMA_p + Expression_p('replacement') + Optional(COMMA_p + Expression_p('flags')) + RPAR_p)
class StrReplaceExpression(SPARQLNonTerminal): pass
if do_parseactions: StrReplaceExpression_p.setName('StrReplaceExpression').setParseAction(__parseInfoFunc((StrReplaceExpression)))
 
# [123]   SubstringExpression       ::=   'SUBSTR' '(' Expression ',' Expression ( ',' Expression )? ')' 
SubstringExpression_p = Group(SUBSTR_kw_p + LPAR_p + Expression_p('source') + COMMA_p + Expression_p('startloc') + Optional(COMMA_p + Expression_p('length')) + RPAR_p)
class SubstringExpression(SPARQLNonTerminal): pass
if do_parseactions: SubstringExpression_p.setName('SubstringExpression').setParseAction(__parseInfoFunc((SubstringExpression)))
 
# [122]   RegexExpression   ::=   'REGEX' '(' Expression ',' Expression ( ',' Expression )? ')' 
RegexExpression_p = Group(REGEX_kw_p + LPAR_p + Expression_p('text') + COMMA_p + Expression_p('pattern') + Optional(COMMA_p + Expression_p('flags')) + RPAR_p)
class RegexExpression(SPARQLNonTerminal): pass
if do_parseactions: RegexExpression_p.setName('RegexExpression').setParseAction(__parseInfoFunc((RegexExpression)))

# [108]   Var       ::=   VAR1 | VAR2 
Var_p = Group(VAR1_p | VAR2_p)
class Var(SPARQLNonTerminal): pass
if do_parseactions: Var_p.setName('Var').setParseAction(__parseInfoFunc((Var)))

ExpressionList_p = Forward()
class ExpressionList(SPARQLNonTerminal): pass
if do_parseactions: ExpressionList_p.setName('ExpressionList').setParseAction(__parseInfoFunc((ExpressionList)))


# [121]   BuiltInCall       ::=     Aggregate 
#             | 'STR' '(' Expression ')' 
#             | 'LANG' '(' Expression ')' 
#             | 'LANGMATCHES' '(' Expression ',' Expression ')' 
#             | 'DATATYPE' '(' Expression ')' 
#             | 'BOUND' '(' Var ')' 
#             | 'IRI' '(' Expression ')' 
#             | 'URI' '(' Expression ')' 
#             | 'BNODE' ( '(' Expression ')' | NIL ) 
#             | 'RAND' NIL 
#             | 'ABS' '(' Expression ')' 
#             | 'CEIL' '(' Expression ')' 
#             | 'FLOOR' '(' Expression ')' 
#             | 'ROUND' '(' Expression ')' 
#             | 'CONCAT' ExpressionList 
#             | SubstringExpression 
#             | 'STRLEN' '(' Expression ')' 
#             | StrReplaceExpression 
#             | 'UCASE' '(' Expression ')' 
#             | 'LCASE' '(' Expression ')' 
#             | 'ENCODE_FOR_URI' '(' Expression ')' 
#             | 'CONTAINS' '(' Expression ',' Expression ')' 
#             | 'STRSTARTS' '(' Expression ',' Expression ')' 
#             | 'STRENDS' '(' Expression ',' Expression ')' 
#             | 'STRBEFORE' '(' Expression ',' Expression ')' 
#             | 'STRAFTER' '(' Expression ',' Expression ')' 
#             | 'YEAR' '(' Expression ')' 
#             | 'MONTH' '(' Expression ')' 
#             | 'DAY' '(' Expression ')' 
#             | 'HOURS' '(' Expression ')' 
#             | 'MINUTES' '(' Expression ')' 
#             | 'SECONDS' '(' Expression ')' 
#             | 'TIMEZONE' '(' Expression ')' 
#             | 'TZ' '(' Expression ')' 
#             | 'NOW' NIL 
#             | 'UUID' NIL 
#             | 'STRUUID' NIL 
#             | 'MD5' '(' Expression ')' 
#             | 'SHA1' '(' Expression ')' 
#             | 'SHA256' '(' Expression ')' 
#             | 'SHA384' '(' Expression ')' 
#             | 'SHA512' '(' Expression ')' 
#             | 'COALESCE' ExpressionList 
#             | 'IF' '(' Expression ',' Expression ',' Expression ')' 
#             | 'STRLANG' '(' Expression ',' Expression ')' 
#             | 'STRDT' '(' Expression ',' Expression ')' 
#             | 'sameTerm' '(' Expression ',' Expression ')' 
#             | 'isIRI' '(' Expression ')' 
#             | 'isURI' '(' Expression ')' 
#             | 'isBLANK' '(' Expression ')' 
#             | 'isLITERAL' '(' Expression ')' 
#             | 'isNUMERIC' '(' Expression ')' 
#             | RegexExpression 
#             | ExistsFunc 
#             | NotExistsFunc 
BuiltInCall_p = Group(Aggregate_p | \
                STR_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                LANG_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                LANGMATCHES_kw_p + LPAR_p + Expression_p('language-tag') + COMMA_p + Expression_p('language-range') + RPAR_p    | \
                DATATYPE_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                BOUND_kw_p + LPAR_p + Var_p('var') + RPAR_p    | \
                IRI_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                URI_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                BNODE_kw_p + (LPAR_p + Expression_p('expression') + RPAR_p | NIL_p)    | \
                RAND_kw_p + NIL_p    | \
                ABS_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                CEIL_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                FLOOR_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                ROUND_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                CONCAT_kw_p + ExpressionList_p('expressionList')    | \
                SubstringExpression_p   | \
                STRLEN_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                StrReplaceExpression_p  | \
                UCASE_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                LCASE_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                ENCODE_FOR_URI_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                CONTAINS_kw_p + LPAR_p + Expression_p('arg1') + COMMA_p + Expression_p('arg2') + RPAR_p    | \
                STRSTARTS_kw_p + LPAR_p + Expression_p('arg1') + COMMA_p + Expression_p('arg2') + RPAR_p    | \
                STRENDS_kw_p + LPAR_p + Expression_p('arg1') + COMMA_p + Expression_p('arg2') + RPAR_p    | \
                STRBEFORE_kw_p + LPAR_p + Expression_p('arg1') + COMMA_p + Expression_p('arg2') + RPAR_p    | \
                STRAFTER_kw_p + LPAR_p + Expression_p('arg1') + COMMA_p + Expression_p('arg2') + RPAR_p    | \
                YEAR_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                MONTH_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                DAY_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                HOURS_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                MINUTES_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                SECONDS_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                TIMEZONE_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                TZ_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                NOW_kw_p + NIL_p    | \
                UUID_kw_p + NIL_p    | \
                STRUUID_kw_p + NIL_p    | \
                MD5_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                SHA1_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                SHA256_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                SHA384_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                SHA512_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                COALESCE_kw_p + ExpressionList_p('expressionList')    | \
                IF_kw_p + LPAR_p + Expression_p('expression1') + COMMA_p + Expression_p('expression2') + COMMA_p + Expression_p('expression3') + RPAR_p    | \
                STRLANG_kw_p + LPAR_p + Expression_p('lexicalForm') + COMMA_p + Expression_p('langTag') + RPAR_p    | \
                STRDT_kw_p + LPAR_p + Expression_p('lexicalForm') + COMMA_p + Expression_p('datatypeIRI') + RPAR_p    | \
                sameTerm_kw_p + LPAR_p + Expression_p('term1') + COMMA_p + Expression_p('term2') + RPAR_p    | \
                isIRI_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                isURI_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                isBLANK_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                isLITERAL_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                isNUMERIC_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                RegexExpression_p | \
                ExistsFunc_p | \
                NotExistsFunc_p )
class BuiltInCall(SPARQLNonTerminal): pass
if do_parseactions: BuiltInCall_p.setName('BuiltInCall').setParseAction(__parseInfoFunc((BuiltInCall)))

# [120]   BrackettedExpression      ::=   '(' Expression ')' 
BracketedExpression_p = Group(LPAR_p + Expression_p('expression') + RPAR_p)
class BracketedExpression(SPARQLNonTerminal): pass
if do_parseactions: BracketedExpression_p.setName('BracketedExpression').setParseAction(__parseInfoFunc((BracketedExpression)))

# [119]   PrimaryExpression         ::=   BrackettedExpression | BuiltInCall | iriOrFunction | RDFLiteral | NumericLiteral | BooleanLiteral | Var 
PrimaryExpression_p = Group(BracketedExpression_p | BuiltInCall_p | iriOrFunction_p('iriOrFunction') | RDFLiteral_p | NumericLiteral_p | BooleanLiteral_p | Var_p)
class PrimaryExpression(SPARQLNonTerminal): pass
if do_parseactions: PrimaryExpression_p.setName('PrimaryExpression').setParseAction(__parseInfoFunc((PrimaryExpression)))

# [118]   UnaryExpression   ::=     '!' PrimaryExpression 
#             | '+' PrimaryExpression 
#             | '-' PrimaryExpression 
#             | PrimaryExpression 
UnaryExpression_p = Group(NOT_op_p + PrimaryExpression_p | PLUS_op_p + PrimaryExpression_p | MINUS_op_p + PrimaryExpression_p | PrimaryExpression_p)
class UnaryExpression(SPARQLNonTerminal): pass
if do_parseactions: UnaryExpression_p.setName('UnaryExpression').setParseAction(__parseInfoFunc((UnaryExpression)))

# [117]   MultiplicativeExpression          ::=   UnaryExpression ( '*' UnaryExpression | '/' UnaryExpression )* 
MultiplicativeExpression_p = Group(UnaryExpression_p + ZeroOrMore( TIMES_op_p + UnaryExpression_p | DIV_op_p + UnaryExpression_p ))
class MultiplicativeExpression(SPARQLNonTerminal): pass
if do_parseactions: MultiplicativeExpression_p.setName('MultiplicativeExpression').setParseAction(__parseInfoFunc((MultiplicativeExpression)))

# [116]   AdditiveExpression        ::=   MultiplicativeExpression ( '+' MultiplicativeExpression | '-' MultiplicativeExpression | ( NumericLiteralPositive | NumericLiteralNegative ) ( ( '*' UnaryExpression ) | ( '/' UnaryExpression ) )* )* 
AdditiveExpression_p = Group(MultiplicativeExpression_p + ZeroOrMore (PLUS_op_p + MultiplicativeExpression_p | MINUS_op_p  + MultiplicativeExpression_p | (NumericLiteralPositive_p | NumericLiteralNegative_p) + ZeroOrMore (TIMES_op_p + UnaryExpression_p | DIV_op_p + UnaryExpression_p)))
class AdditiveExpression(SPARQLNonTerminal): pass
if do_parseactions: AdditiveExpression_p.setName('AdditiveExpression').setParseAction(__parseInfoFunc((AdditiveExpression)))

# [115]   NumericExpression         ::=   AdditiveExpression 
NumericExpression_p = Group(AdditiveExpression_p + Empty())
class NumericExpression(SPARQLNonTerminal): pass
if do_parseactions: NumericExpression_p.setName('NumericExpression').setParseAction(__parseInfoFunc((NumericExpression)))

# [114]   RelationalExpression      ::=   NumericExpression ( '=' NumericExpression | '!=' NumericExpression | '<' NumericExpression | '>' NumericExpression | '<=' NumericExpression | '>=' NumericExpression | 'IN' ExpressionList | 'NOT' 'IN' ExpressionList )? 
RelationalExpression_p = Group(NumericExpression_p + Optional( EQ_op_p + NumericExpression_p | \
                                                         NE_op_p + NumericExpression_p | \
                                                         LT_op_p + NumericExpression_p | \
                                                         GT_op_p + NumericExpression_p | \
                                                         LE_op_p + NumericExpression_p | \
                                                         GE_op_p + NumericExpression_p | \
                                                         IN_kw_p + ExpressionList_p | \
                                                         NOT_IN_kw_p + ExpressionList_p) )
class RelationalExpression(SPARQLNonTerminal): pass
if do_parseactions: RelationalExpression_p.setName('RelationalExpression').setParseAction(__parseInfoFunc((RelationalExpression)))

# [113]   ValueLogical      ::=   RelationalExpression 
ValueLogical_p = Group(RelationalExpression_p + Empty())
class ValueLogical(SPARQLNonTerminal): pass
if do_parseactions: ValueLogical_p.setName('ValueLogical').setParseAction(__parseInfoFunc((ValueLogical)))

# [112]   ConditionalAndExpression          ::=   ValueLogical ( '&&' ValueLogical )* 
ConditionalAndExpression_p = Group(ValueLogical_p + ZeroOrMore(AND_op_p + ValueLogical_p))
class ConditionalAndExpression(SPARQLNonTerminal): pass
if do_parseactions: ConditionalAndExpression_p.setName('ConditionalAndExpression').setParseAction(__parseInfoFunc((ConditionalAndExpression)))

# [111]   ConditionalOrExpression   ::=   ConditionalAndExpression ( '||' ConditionalAndExpression )* 
ConditionalOrExpression_p = Group(ConditionalAndExpression_p + ZeroOrMore(OR_op_p + ConditionalAndExpression_p))
class ConditionalOrExpression(SPARQLNonTerminal): pass
if do_parseactions: ConditionalOrExpression_p.setName('ConditionalOrExpression').setParseAction(__parseInfoFunc((ConditionalOrExpression)))

# [110]   Expression        ::=   ConditionalOrExpression 
Expression_p << Group(ConditionalOrExpression_p + Empty())

# [109]   GraphTerm         ::=   iri | RDFLiteral | NumericLiteral | BooleanLiteral | BlankNode | NIL 
GraphTerm_p =   Group(iri_p | \
                RDFLiteral_p | \
                NumericLiteral_p | \
                BooleanLiteral_p | \
                BlankNode_p | \
                NIL_p )
class GraphTerm(SPARQLNonTerminal): pass
if do_parseactions: GraphTerm_p.setName('GraphTerm').setParseAction(__parseInfoFunc((GraphTerm)))
                
# [107]   VarOrIri          ::=   Var | iri 
VarOrIri_p = Group(Var_p | iri_p)
class VarOrIri(SPARQLNonTerminal): pass
if do_parseactions: VarOrIri_p.setName('VarOrIri').setParseAction(__parseInfoFunc((VarOrIri)))

# [106]   VarOrTerm         ::=   Var | GraphTerm 
VarOrTerm_p = Group(Var_p | GraphTerm_p)
class VarOrTerm(SPARQLNonTerminal): pass
if do_parseactions: VarOrTerm_p.setName('VarOrTerm').setParseAction(__parseInfoFunc((VarOrTerm)))

TriplesNodePath_p = Forward()
class TriplesNodePath(SPARQLNonTerminal): pass
if do_parseactions: TriplesNodePath_p.setName('TriplesNodePath').setParseAction(__parseInfoFunc((TriplesNodePath)))

# [105]   GraphNodePath     ::=   VarOrTerm | TriplesNodePath 
GraphNodePath_p = Group(VarOrTerm_p ^ TriplesNodePath_p )

TriplesNode_p = Forward()
class TriplesNode(SPARQLNonTerminal): pass
if do_parseactions: TriplesNode_p.setName('TriplesNode').setParseAction(__parseInfoFunc((TriplesNode)))

# [104]   GraphNode         ::=   VarOrTerm | TriplesNode 
GraphNode_p = Group(VarOrTerm_p ^ TriplesNode_p)
class GraphNode(SPARQLNonTerminal): pass
if do_parseactions: GraphNode_p.setName('GraphNode').setParseAction(__parseInfoFunc((GraphNode)))

# [103]   CollectionPath    ::=   '(' GraphNodePath+ ')' 
CollectionPath_p = Group( LPAR_p + OneOrMore(GraphNodePath_p) + RPAR_p)
class CollectionPath(SPARQLNonTerminal): pass
if do_parseactions: CollectionPath_p.setName('CollectionPath').setParseAction(__parseInfoFunc((CollectionPath)))

# [102]   Collection        ::=   '(' GraphNode+ ')' 
Collection_p = Group( LPAR_p + OneOrMore(GraphNode_p) + RPAR_p)
class Collection(SPARQLNonTerminal): pass
if do_parseactions: Collection_p.setName('Collection').setParseAction(__parseInfoFunc((Collection)))

PropertyListPathNotEmpty_p = Forward()
class PropertyListPathNotEmpty(SPARQLNonTerminal): pass
if do_parseactions: PropertyListPathNotEmpty_p.setName('PropertyListPathNotEmpty').setParseAction(__parseInfoFunc((PropertyListPathNotEmpty)))

# [101]   BlankNodePropertyListPath         ::=   '[' PropertyListPathNotEmpty ']'
BlankNodePropertyListPath_p = Group(  LBRACK_p + PropertyListPathNotEmpty_p + RBRACK_p )
class BlankNodePropertyListPath(SPARQLNonTerminal): pass
if do_parseactions: BlankNodePropertyListPath_p.setName('BlankNodePropertyListPath').setParseAction(__parseInfoFunc((BlankNodePropertyListPath)))

# [100]   TriplesNodePath   ::=   CollectionPath | BlankNodePropertyListPath 
TriplesNodePath_p << Group(CollectionPath_p | BlankNodePropertyListPath_p) 

PropertyListNotEmpty_p = Forward()
class PropertyListNotEmpty(SPARQLNonTerminal): pass
if do_parseactions: PropertyListNotEmpty_p.setName('PropertyListNotEmpty').setParseAction(__parseInfoFunc((PropertyListNotEmpty)))

# [99]    BlankNodePropertyList     ::=   '[' PropertyListNotEmpty ']' 
BlankNodePropertyList_p = Group(  LBRACK_p + PropertyListNotEmpty_p + RBRACK_p )
class BlankNodePropertyList(SPARQLNonTerminal): pass
if do_parseactions: BlankNodePropertyList_p.setName('BlankNodePropertyList').setParseAction(__parseInfoFunc((BlankNodePropertyList)))

# [98]    TriplesNode       ::=   Collection | BlankNodePropertyList 
TriplesNode_p << Group(Collection_p | BlankNodePropertyList_p)

# [97]    Integer   ::=   INTEGER 
Integer_p = Group(INTEGER_p + Empty())
class Integer(SPARQLNonTerminal): pass
if do_parseactions: Integer_p.setName('Integer').setParseAction(__parseInfoFunc((Integer)))

# [96]    PathOneInPropertySet      ::=   iri | 'a' | '^' ( iri | 'a' ) 
PathOneInPropertySet_p = Group(  iri_p | TYPE_kw_p | (INVERSE_op_p  + ( iri_p | TYPE_kw_p )))
class PathOneInPropertySet(SPARQLNonTerminal): pass
if do_parseactions: PathOneInPropertySet_p.setName('PathOneInPropertySet').setParseAction(__parseInfoFunc((PathOneInPropertySet)))

# pattern and class to parse and __str__ delimited PathOneInPropertySet lists
PathOneInPropertySet_list_p = punctuatedList(PathOneInPropertySet_p, delim='|')

# [95]    PathNegatedPropertySet    ::=   PathOneInPropertySet | '(' ( PathOneInPropertySet ( '|' PathOneInPropertySet )* )? ')' 
PathNegatedPropertySet_p = Group(PathOneInPropertySet_p | (LPAR_p + Optional(PathOneInPropertySet_list_p('pathone')) + RPAR_p))
class PathNegatedPropertySet(SPARQLNonTerminal): pass
if do_parseactions: PathNegatedPropertySet_p.setName('PathNegatedPropertySet').setParseAction(__parseInfoFunc((PathNegatedPropertySet)))

Path_p = Forward()
class Path(SPARQLNonTerminal): pass
if do_parseactions: Path_p.setName('Path').setParseAction(__parseInfoFunc((Path)))

# [94]    PathPrimary       ::=   iri | 'a' | '!' PathNegatedPropertySet | '(' Path ')' 
PathPrimary_p = Group(iri_p | TYPE_kw_p | (NOT_op_p + PathNegatedPropertySet_p) | (LPAR_p + Path_p + RPAR_p))
class PathPrimary(SPARQLNonTerminal): pass
if do_parseactions: PathPrimary_p.setName('PathPrimary').setParseAction(__parseInfoFunc((PathPrimary)))

# [93]    PathMod   ::=   '?' | '*' | '+' 
PathMod_p = Group((~VAR1_p + Literal('?')) | Literal('*') | Literal('+'))
class PathMod(SPARQLNonTerminal): pass
if do_parseactions: PathMod_p.setName('PathMod').setParseAction(__parseInfoFunc((PathMod)))

# [91]    PathElt   ::=   PathPrimary PathMod? 
PathElt_p = Group(PathPrimary_p + Optional(PathMod_p) )
class PathElt(SPARQLNonTerminal): pass
if do_parseactions: PathElt_p.setName('PathElt').setParseAction(__parseInfoFunc((PathElt)))

# [92]    PathEltOrInverse          ::=   PathElt | '^' PathElt 
PathEltOrInverse_p = Group(PathElt_p | (INVERSE_op_p + PathElt_p))
class PathEltOrInverse(SPARQLNonTerminal): pass
if do_parseactions: PathEltOrInverse_p.setName('PathEltOrInverse').setParseAction(__parseInfoFunc((PathEltOrInverse)))

# [90]    PathSequence      ::=   PathEltOrInverse ( '/' PathEltOrInverse )* 
PathSequence_p = Group(delimitedList(PathEltOrInverse_p, delim='/'))
class PathSequence(SPARQLNonTerminal):  
    def __str__(self):
        return ' / '.join([v[1] if isinstance(v[1], str) else v[1].__str__() for v in self.getItems()])
if do_parseactions: PathSequence_p.setName('PathSequence').setParseAction(__parseInfoFunc((PathSequence)))

# [89]    PathAlternative   ::=   PathSequence ( '|' PathSequence )* 
PathAlternative_p = Group(delimitedList(PathSequence_p, delim='|'))
class PathAlternative(SPARQLNonTerminal):
    def __str__(self):
        return ' | '.join([v[1] if isinstance(v[1], str) else v[1].__str__() for v in self.getItems()])
if do_parseactions: PathAlternative_p.setName('PathAlternative').setParseAction(__parseInfoFunc((PathAlternative)))
 
# [88]    Path      ::=   PathAlternative
Path_p << Group(PathAlternative_p + Empty()) 

# [87]    ObjectPath        ::=   GraphNodePath 
ObjectPath_p = Group(GraphNodePath_p + Empty() )
class ObjectPath(SPARQLNonTerminal): pass
if do_parseactions: ObjectPath_p.setName('ObjectPath').setParseAction(__parseInfoFunc((ObjectPath)))

# [86]    ObjectListPath    ::=   ObjectPath ( ',' ObjectPath )* 
ObjectListPath_p = Group(delimitedList(ObjectPath_p))
class ObjectListPath(SPARQLNonTerminal):
    def __str__(self):
        return ', '.join([v[1] if isinstance(v[1], str) else v[1].__str__() for v in self.getItems()])
if do_parseactions: ObjectListPath_p.setName('ObjectListPath').setParseAction(__parseInfoFunc((ObjectListPath)))

# [85]    VerbSimple        ::=   Var 
VerbSimple_p = Group(Var_p + Empty() )
class VerbSimple(SPARQLNonTerminal): pass
if do_parseactions: VerbSimple_p.setName('VerbSimple').setParseAction(__parseInfoFunc((VerbSimple)))

# [84]    VerbPath          ::=   Path
VerbPath_p = Group(Path_p + Empty() )
class VerbPath(SPARQLNonTerminal): pass
if do_parseactions: VerbPath_p.setName('VerbPath').setParseAction(__parseInfoFunc((VerbPath)))

# [80]    Object    ::=   GraphNode 
Object_p = Group(GraphNode_p + Empty() )
class Object(SPARQLNonTerminal): pass
if do_parseactions: Object_p.setName('Object').setParseAction(__parseInfoFunc((Object)))
 
# [79]    ObjectList        ::=   Object ( ',' Object )* 
ObjectList_p = Group(delimitedList(Object_p))
class ObjectList(SPARQLNonTerminal):
    def __str__(self):
        return ', '.join([v[1] if isinstance(v[1], str) else v[1].__str__() for v in self.getItems()])
if do_parseactions: ObjectList_p.setName('ObjectList').setParseAction(__parseInfoFunc((ObjectList)))

# [83]    PropertyListPathNotEmpty          ::=   ( VerbPath | VerbSimple ) ObjectListPath ( ';' ( ( VerbPath | VerbSimple ) ObjectList )? )* 
PropertyListPathNotEmpty_p << Group((VerbPath_p | VerbSimple_p) + ObjectListPath_p +  ZeroOrMore(SEMICOL_p + Optional(( VerbPath_p | VerbSimple_p) + ObjectList_p)))

# [82]    PropertyListPath          ::=   PropertyListPathNotEmpty? 
PropertyListPath_p = Group(Optional(PropertyListPathNotEmpty_p))
class PropertyListPath(SPARQLNonTerminal): pass
if do_parseactions: PropertyListPath_p.setName('PropertyListPath').setParseAction(__parseInfoFunc((PropertyListPath)))

# [81]    TriplesSameSubjectPath    ::=   VarOrTerm PropertyListPathNotEmpty | TriplesNodePath PropertyListPath 
TriplesSameSubjectPath_p = Group((VarOrTerm_p + PropertyListPathNotEmpty_p) | (TriplesNodePath_p + PropertyListPath_p))
class TriplesSameSubjectPath(SPARQLNonTerminal): pass
if do_parseactions: TriplesSameSubjectPath_p.setName('TriplesSameSubjectPath').setParseAction(__parseInfoFunc((TriplesSameSubjectPath)))

# [78]    Verb      ::=   VarOrIri | 'a' 
Verb_p = Group(VarOrIri_p | TYPE_kw_p)
class Verb(SPARQLNonTerminal): pass
if do_parseactions: Verb_p.setName('Verb').setParseAction(__parseInfoFunc((Verb)))

# [77]    PropertyListNotEmpty      ::=   Verb ObjectList ( ';' ( Verb ObjectList )? )* 
PropertyListNotEmpty_p << Group(Verb_p + ObjectList_p + ZeroOrMore(SEMICOL_p + Optional(Verb_p + ObjectList_p))) 

# [76]    PropertyList      ::=   PropertyListNotEmpty?
PropertyList_p = Group(Optional(PropertyListNotEmpty_p) )
class PropertyList(SPARQLNonTerminal): pass
if do_parseactions: PropertyList_p.setName('PropertyList').setParseAction(__parseInfoFunc((PropertyList)))

# [75]    TriplesSameSubject        ::=   VarOrTerm PropertyListNotEmpty | TriplesNode PropertyList
TriplesSameSubject_p = Group((VarOrTerm_p + PropertyListNotEmpty_p) | (TriplesNode_p + PropertyList_p) )
class TriplesSameSubject(SPARQLNonTerminal): pass
if do_parseactions: TriplesSameSubject_p.setName('TriplesSameSubject').setParseAction(__parseInfoFunc((TriplesSameSubject)))

# pattern and class to parse and __str__ delimited TriplesSameSubject lists
TriplesSameSubject_list_p = punctuatedList(TriplesSameSubject_p, delim='.')

# [74]    ConstructTriples          ::=   TriplesSameSubject ( '.' ConstructTriples? )? 
ConstructTriples_p = Group(TriplesSameSubject_list_p + Optional(PERIOD_p))
class ConstructTriples(SPARQLNonTerminal): pass
if do_parseactions: ConstructTriples_p.setName('ConstructTriples').setParseAction(__parseInfoFunc((ConstructTriples)))

# [73]    ConstructTemplate         ::=   '{' ConstructTriples? '}'
ConstructTemplate_p = Group(  LCURL_p + Optional(ConstructTriples_p) + RCURL_p )
class ConstructTemplate(SPARQLNonTerminal): pass
if do_parseactions: ConstructTemplate_p.setName('ConstructTemplate').setParseAction(__parseInfoFunc((ConstructTemplate)))

# [72]    ExpressionList    ::=   NIL | '(' Expression ( ',' Expression )* ')' 
ExpressionList_p << Group(NIL_p | (LPAR_p + Expression_list_p + RPAR_p))

# [70]    FunctionCall      ::=   iri ArgList 
FunctionCall_p = Group(iri_p + ArgList_p)
class FunctionCall(SPARQLNonTerminal): pass
if do_parseactions: FunctionCall_p.setName('FunctionCall').setParseAction(__parseInfoFunc((FunctionCall)))

# [69]    Constraint        ::=   BrackettedExpression | BuiltInCall | FunctionCall 
Constraint_p = Group(BracketedExpression_p | BuiltInCall_p | FunctionCall_p)
class Constraint(SPARQLNonTerminal): pass
if do_parseactions: Constraint_p.setName('Constraint').setParseAction(__parseInfoFunc((Constraint)))

# [68]    Filter    ::=   'FILTER' Constraint
Filter_p = Group(FILTER_kw_p + Constraint_p )
class Filter(SPARQLNonTerminal): pass
if do_parseactions: Filter_p.setName('Filter').setParseAction(__parseInfoFunc((Filter)))

# [67]    GroupOrUnionGraphPattern          ::=   GroupGraphPattern ( 'UNION' GroupGraphPattern )* 
GroupOrUnionGraphPattern_p = Group(GroupGraphPattern_p + ZeroOrMore(UNION_kw_p + GroupGraphPattern_p) )
class GroupOrUnionGraphPattern(SPARQLNonTerminal): pass
if do_parseactions: GroupOrUnionGraphPattern_p.setName('GroupOrUnionGraphPattern').setParseAction(__parseInfoFunc((GroupOrUnionGraphPattern)))

# [66]    MinusGraphPattern         ::=   'MINUS' GroupGraphPattern
MinusGraphPattern_p = Group(  MINUS_kw_p + GroupGraphPattern_p )
class MinusGraphPattern(SPARQLNonTerminal): pass
if do_parseactions: MinusGraphPattern_p.setName('MinusGraphPattern').setParseAction(__parseInfoFunc((MinusGraphPattern)))

# [65]    DataBlockValue    ::=   iri | RDFLiteral | NumericLiteral | BooleanLiteral | 'UNDEF' 
DataBlockValue_p = Group(iri_p | RDFLiteral_p | NumericLiteral_p | BooleanLiteral_p | UNDEF_kw_p)
class DataBlockValue(SPARQLNonTerminal): pass
if do_parseactions: DataBlockValue_p.setName('DataBlockValue').setParseAction(__parseInfoFunc((DataBlockValue)))

# [64]    InlineDataFull    ::=   ( NIL | '(' Var* ')' ) '{' ( '(' DataBlockValue* ')' | NIL )* '}' 
InlineDataFull_p = Group(( NIL_p | (LPAR_p + ZeroOrMore(Var_p) + RPAR_p)) + LCURL_p +  ZeroOrMore((LPAR_p + ZeroOrMore(DataBlockValue_p) + RPAR_p) | NIL_p) + RCURL_p )
class InlineDataFull(SPARQLNonTerminal): pass
if do_parseactions: InlineDataFull_p.setName('InlineDataFull').setParseAction(__parseInfoFunc((InlineDataFull)))

# [63]    InlineDataOneVar          ::=   Var '{' DataBlockValue* '}' 
InlineDataOneVar_p = Group(Var_p + LCURL_p + ZeroOrMore(DataBlockValue_p) + RCURL_p )
class InlineDataOneVar(SPARQLNonTerminal): pass
if do_parseactions: InlineDataOneVar_p.setName('InlineDataOneVar').setParseAction(__parseInfoFunc((InlineDataOneVar)))

# [62]    DataBlock         ::=   InlineDataOneVar | InlineDataFull 
DataBlock_p = Group(InlineDataOneVar_p | InlineDataFull_p)
class DataBlock(SPARQLNonTerminal): pass
if do_parseactions: DataBlock_p.setName('DataBlock').setParseAction(__parseInfoFunc((DataBlock)))

# [61]    InlineData        ::=   'VALUES' DataBlock 
InlineData_p = Group(VALUES_kw_p + DataBlock_p )
class InlineData(SPARQLNonTerminal): pass
if do_parseactions: InlineData_p.setName('InlineData').setParseAction(__parseInfoFunc((InlineData)))

# [60]    Bind      ::=   'BIND' '(' Expression 'AS' Var ')' 
Bind_p = Group(  BIND_kw_p + LPAR_p + Expression_p + AS_kw_p + Var_p + RPAR_p )
class Bind(SPARQLNonTerminal): pass
if do_parseactions: Bind_p.setName('Bind').setParseAction(__parseInfoFunc((Bind)))

# [59]    ServiceGraphPattern       ::=   'SERVICE' 'SILENT'? VarOrIri GroupGraphPattern 
ServiceGraphPattern_p = Group(  SERVICE_kw_p + Optional(SILENT_kw_p) + VarOrIri_p + GroupGraphPattern_p )
class ServiceGraphPattern(SPARQLNonTerminal): pass
if do_parseactions: ServiceGraphPattern_p.setName('ServiceGraphPattern').setParseAction(__parseInfoFunc((ServiceGraphPattern)))

# [58]    GraphGraphPattern         ::=   'GRAPH' VarOrIri GroupGraphPattern 
GraphGraphPattern_p = Group(  GRAPH_kw_p + VarOrIri_p + GroupGraphPattern_p )
class GraphGraphPattern(SPARQLNonTerminal): pass
if do_parseactions: GraphGraphPattern_p.setName('GraphGraphPattern').setParseAction(__parseInfoFunc((GraphGraphPattern)))

# [57]    OptionalGraphPattern      ::=   'OPTIONAL' GroupGraphPattern 
OptionalGraphPattern_p = Group(  OPTIONAL_kw_p + GroupGraphPattern_p )
class OptionalGraphPattern(SPARQLNonTerminal): pass
if do_parseactions: OptionalGraphPattern_p.setName('OptionalGraphPattern').setParseAction(__parseInfoFunc((OptionalGraphPattern)))

# [56]    GraphPatternNotTriples    ::=   GroupOrUnionGraphPattern | OptionalGraphPattern | MinusGraphPattern | GraphGraphPattern | ServiceGraphPattern | Filter | Bind | InlineData 
GraphPatternNotTriples_p = Group(GroupOrUnionGraphPattern_p | OptionalGraphPattern_p | MinusGraphPattern_p | GraphGraphPattern_p | ServiceGraphPattern_p | Filter_p | Bind_p | InlineData_p )
class GraphPatternNotTriples(SPARQLNonTerminal): pass
if do_parseactions: GraphPatternNotTriples_p.setName('GraphPatternNotTriples').setParseAction(__parseInfoFunc((GraphPatternNotTriples)))

# pattern and class to parse and __str__ delimited TriplesSameSubjectPath lists
TriplesSameSubjectPath_list_p = punctuatedList(TriplesSameSubjectPath_p, delim='.')
                                           
# [55]    TriplesBlock      ::=   TriplesSameSubjectPath ( '.' TriplesBlock? )? 
TriplesBlock_p = Group(TriplesSameSubjectPath_list_p('subjpath') + Optional(PERIOD_p))
class TriplesBlock(SPARQLNonTerminal): pass
if do_parseactions: TriplesBlock_p.setName('TriplesBlock').setParseAction(__parseInfoFunc((TriplesBlock)))

# [54]    GroupGraphPatternSub      ::=   TriplesBlock? ( GraphPatternNotTriples '.'? TriplesBlock? )* 
GroupGraphPatternSub_p = Group(Optional(TriplesBlock_p) + ZeroOrMore(GraphPatternNotTriples_p + Optional(PERIOD_p) + Optional(TriplesBlock_p)) )
class GroupGraphPatternSub(SPARQLNonTerminal): pass
if do_parseactions: GroupGraphPatternSub_p.setName('GroupGraphPatternSub').setParseAction(__parseInfoFunc((GroupGraphPatternSub)))

SubSelect_p = Forward()
class SubSelect(SPARQLNonTerminal): pass
if do_parseactions: SubSelect_p.setName('SubSelect').setParseAction(__parseInfoFunc((SubSelect)))

# [53]    GroupGraphPattern         ::=   '{' ( SubSelect | GroupGraphPatternSub ) '}' 
GroupGraphPattern_p << Group(LCURL_p + (SubSelect_p | GroupGraphPatternSub_p)('pattern') + RCURL_p) 

# [52]    TriplesTemplate   ::=   TriplesSameSubject ( '.' TriplesTemplate? )? 
TriplesTemplate_p = Group(TriplesSameSubject_list_p + Optional(PERIOD_p)) 
class TriplesTemplate(SPARQLNonTerminal): pass
if do_parseactions: TriplesTemplate_p.setName('TriplesTemplate').setParseAction(__parseInfoFunc((TriplesTemplate)))

# [51]    QuadsNotTriples   ::=   'GRAPH' VarOrIri '{' TriplesTemplate? '}' 
QuadsNotTriples_p = Group(GRAPH_kw_p + VarOrIri_p + LCURL_p + Optional(TriplesTemplate_p) + RCURL_p )
class QuadsNotTriples(SPARQLNonTerminal): pass
if do_parseactions: QuadsNotTriples_p.setName('QuadsNotTriples').setParseAction(__parseInfoFunc((QuadsNotTriples)))

# [50]    Quads     ::=   TriplesTemplate? ( QuadsNotTriples '.'? TriplesTemplate? )* 
Quads_p = Group(Optional(TriplesTemplate_p) + ZeroOrMore(QuadsNotTriples_p + Optional(PERIOD_p) + Optional(TriplesTemplate_p)) )
class Quads(SPARQLNonTerminal): pass
if do_parseactions: Quads_p.setName('Quads').setParseAction(__parseInfoFunc((Quads)))

# [49]    QuadData          ::=   '{' Quads '}' 
QuadData_p = Group(LCURL_p + Quads_p + RCURL_p )
class QuadData(SPARQLNonTerminal): pass
if do_parseactions: QuadData_p.setName('QuadData').setParseAction(__parseInfoFunc((QuadData)))

# [48]    QuadPattern       ::=   '{' Quads '}' 
QuadPattern_p = Group(LCURL_p + Quads_p + RCURL_p )
class QuadPattern(SPARQLNonTerminal): pass
if do_parseactions: QuadPattern_p.setName('QuadPattern').setParseAction(__parseInfoFunc((QuadPattern)))

# [46]    GraphRef          ::=   'GRAPH' iri 
GraphRef_p = Group(GRAPH_kw_p + iri_p )
class GraphRef(SPARQLNonTerminal): pass
if do_parseactions: GraphRef_p.setName('GraphRef').setParseAction(__parseInfoFunc((GraphRef)))

# [47]    GraphRefAll       ::=   GraphRef | 'DEFAULT' | 'NAMED' | 'ALL' 
GraphRefAll_p = Group(GraphRef_p | DEFAULT_kw_p | NAMED_kw_p | ALL_kw_p )
class GraphRefAll(SPARQLNonTerminal): pass
if do_parseactions: GraphRefAll_p.setName('GraphRefAll').setParseAction(__parseInfoFunc((GraphRefAll)))

# [45]    GraphOrDefault    ::=   'DEFAULT' | 'GRAPH'? iri 
GraphOrDefault_p = Group(  DEFAULT_kw_p | (Optional(GRAPH_kw_p) + iri_p) )
class GraphOrDefault(SPARQLNonTerminal): pass
if do_parseactions: GraphOrDefault_p.setName('GraphOrDefault').setParseAction(__parseInfoFunc((GraphOrDefault)))

# [44]    UsingClause       ::=   'USING' ( iri | 'NAMED' iri ) 
UsingClause_p = Group(  USING_kw_p + (iri_p | (NAMED_kw_p + iri_p)) )
class UsingClause(SPARQLNonTerminal): pass
if do_parseactions: UsingClause_p.setName('UsingClause').setParseAction(__parseInfoFunc((UsingClause)))

# [43]    InsertClause      ::=   'INSERT' QuadPattern 
InsertClause_p = Group(  INSERT_kw_p + QuadPattern_p )
class InsertClause(SPARQLNonTerminal): pass
if do_parseactions: InsertClause_p.setName('InsertClause').setParseAction(__parseInfoFunc((InsertClause)))

# [42]    DeleteClause      ::=   'DELETE' QuadPattern 
DeleteClause_p = Group(  DELETE_kw_p + QuadPattern_p )
class DeleteClause(SPARQLNonTerminal): pass
if do_parseactions: DeleteClause_p.setName('DeleteClause').setParseAction(__parseInfoFunc((DeleteClause)))

# [41]    Modify    ::=   ( 'WITH' iri )? ( DeleteClause InsertClause? | InsertClause ) UsingClause* 'WHERE' GroupGraphPattern 
Modify_p = Group(  Optional(WITH_kw_p + iri_p) + ( (DeleteClause_p + Optional(InsertClause_p) ) | InsertClause_p ) + ZeroOrMore(UsingClause_p) + WHERE_kw_p + GroupGraphPattern_p )
class Modify(SPARQLNonTerminal): pass
if do_parseactions: Modify_p.setName('Modify').setParseAction(__parseInfoFunc((Modify)))

# [40]    DeleteWhere       ::=   'DELETE WHERE' QuadPattern 
DeleteWhere_p = Group(  DELETE_WHERE_kw_p + QuadPattern_p )
class DeleteWhere(SPARQLNonTerminal): pass
if do_parseactions: DeleteWhere_p.setName('DeleteWhere').setParseAction(__parseInfoFunc((DeleteWhere)))

# [39]    DeleteData        ::=   'DELETE DATA' QuadData 
DeleteData_p = Group(DELETE_DATA_kw_p + QuadData_p )
class DeleteData(SPARQLNonTerminal): pass
if do_parseactions: DeleteData_p.setName('DeleteData').setParseAction(__parseInfoFunc((DeleteData)))

# [38]    InsertData        ::=   'INSERT DATA' QuadData 
InsertData_p = Group(INSERT_DATA_kw_p + QuadData_p )
class InsertData(SPARQLNonTerminal): pass
if do_parseactions: InsertData_p.setName('InsertData').setParseAction(__parseInfoFunc((InsertData)))

# [37]    Copy      ::=   'COPY' 'SILENT'? GraphOrDefault 'TO' GraphOrDefault 
Copy_p = Group(COPY_kw_p + Optional(SILENT_kw_p) + GraphOrDefault_p + TO_kw_p + GraphOrDefault_p )
class Copy(SPARQLNonTerminal): pass
if do_parseactions: Copy_p.setName('Copy').setParseAction(__parseInfoFunc((Copy)))

# [36]    Move      ::=   'MOVE' 'SILENT'? GraphOrDefault 'TO' GraphOrDefault 
Move_p = Group(MOVE_kw_p + Optional(SILENT_kw_p) + GraphOrDefault_p + TO_kw_p + GraphOrDefault_p )
class Move(SPARQLNonTerminal): pass
if do_parseactions: Move_p.setName('Move').setParseAction(__parseInfoFunc((Move)))

# [35]    Add       ::=   'ADD' 'SILENT'? GraphOrDefault 'TO' GraphOrDefault 
Add_p = Group(ADD_kw_p + Optional(SILENT_kw_p) + GraphOrDefault_p + TO_kw_p + GraphOrDefault_p )
class Add(SPARQLNonTerminal): pass
if do_parseactions: Add_p.setName('Add').setParseAction(__parseInfoFunc((Add)))

# [34]    Create    ::=   'CREATE' 'SILENT'? GraphRef 
Create_p = Group(CREATE_kw_p + Optional(SILENT_kw_p) + GraphRef_p)
class Create(SPARQLNonTerminal): pass
if do_parseactions: Create_p.setName('Create').setParseAction(__parseInfoFunc((Create)))

# [33]    Drop      ::=   'DROP' 'SILENT'? GraphRefAll 
Drop_p = Group(DROP_kw_p + Optional(SILENT_kw_p) + GraphRefAll_p)
class Drop(SPARQLNonTerminal): pass
if do_parseactions: Drop_p.setName('Drop').setParseAction(__parseInfoFunc((Drop)))

# [32]    Clear     ::=   'CLEAR' 'SILENT'? GraphRefAll 
Clear_p = Group(CLEAR_kw_p + Optional(SILENT_kw_p) + GraphRefAll_p )
class Clear(SPARQLNonTerminal): pass
if do_parseactions: Clear_p.setName('Clear').setParseAction(__parseInfoFunc((Clear)))

# [31]    Load      ::=   'LOAD' 'SILENT'? iri ( 'INTO' GraphRef )? 
Load_p = Group(LOAD_kw_p + Optional(SILENT_kw_p) + iri_p  + Optional(INTO_kw_p + GraphRef_p))
class Load(SPARQLNonTerminal): pass
if do_parseactions: Load_p.setName('Load').setParseAction(__parseInfoFunc((Load)))

# [30]    Update1   ::=   Load | Clear | Drop | Add | Move | Copy | Create | InsertData | DeleteData | DeleteWhere | Modify 
Update1_p = Group(Load_p | Clear_p | Drop_p | Add_p | Move_p | Copy_p | Create_p | InsertData_p | DeleteData_p | DeleteWhere_p | Modify_p )
class Update1(SPARQLNonTerminal): pass
if do_parseactions: Update1_p.setParseAction(__parseInfoFunc(Update1))

Prologue_p = Forward()
class Prologue(SPARQLNonTerminal): pass
if do_parseactions: Prologue_p.setName('Prologue').setParseAction(__parseInfoFunc((Prologue)))

Update_p = Forward()
class Update(SPARQLNonTerminal): pass
if do_parseactions: Update_p.setName('Update').setParseAction(__parseInfoFunc((Update)))

# [29]    Update    ::=   Prologue ( Update1 ( ';' Update )? )? 
Update_p << Group(Prologue_p + Optional(Update1_p + Optional(SEMICOL_p + Update_p))) 

# [28]    ValuesClause      ::=   ( 'VALUES' DataBlock )? 
ValuesClause_p = Group(Optional(VALUES_kw_p + DataBlock_p) )
class ValuesClause(SPARQLNonTerminal): pass
if do_parseactions: ValuesClause_p.setName('ValuesClause').setParseAction(__parseInfoFunc((ValuesClause)))

# [27]    OffsetClause      ::=   'OFFSET' INTEGER 
OffsetClause_p = Group(  OFFSET_kw_p + INTEGER_p )
class OffsetClause(SPARQLNonTerminal): pass
if do_parseactions: OffsetClause_p.setName('OffsetClause').setParseAction(__parseInfoFunc((OffsetClause)))

# [26]    LimitClause       ::=   'LIMIT' INTEGER 
LimitClause_p = Group(  LIMIT_kw_p + INTEGER_p )
class LimitClause(SPARQLNonTerminal): pass
if do_parseactions: LimitClause_p.setName('LimitClause').setParseAction(__parseInfoFunc((LimitClause)))

# [25]    LimitOffsetClauses        ::=   LimitClause OffsetClause? | OffsetClause LimitClause? 
LimitOffsetClauses_p = Group(LimitClause_p + Optional(OffsetClause_p)) | (OffsetClause_p + Optional(LimitClause_p))
class LimitOffsetClauses(SPARQLNonTerminal): pass
if do_parseactions: LimitOffsetClauses_p.setName('LimitOffsetClauses').setParseAction(__parseInfoFunc((LimitOffsetClauses)))

# [24]    OrderCondition    ::=   ( ( 'ASC' | 'DESC' ) BrackettedExpression ) | ( Constraint | Var ) 
OrderCondition_p =   Group((ASC_kw_p | DESC_kw_p) + BracketedExpression_p) | (Constraint_p | Var_p)
class OrderCondition(SPARQLNonTerminal): pass
if do_parseactions: OrderCondition_p.setName('OrderCondition').setParseAction(__parseInfoFunc((OrderCondition)))

# [23]    OrderClause       ::=   'ORDER' 'BY' OrderCondition+ 
OrderClause_p = Group(ORDER_BY_kw_p + OneOrMore(OrderCondition_p) )
class OrderClause(SPARQLNonTerminal): pass
if do_parseactions: OrderClause_p.setName('OrderClause').setParseAction(__parseInfoFunc((OrderClause)))

# [22]    HavingCondition   ::=   Constraint 
HavingCondition_p = Group(Constraint_p)
class HavingCondition(SPARQLNonTerminal): pass
if do_parseactions: HavingCondition_p.setName('HavingCondition').setParseAction(__parseInfoFunc((HavingCondition)))

# [21]    HavingClause      ::=   'HAVING' HavingCondition+ 
HavingClause_p = Group(HAVING_kw_p + OneOrMore(HavingCondition_p) )
class HavingClause(SPARQLNonTerminal): pass
if do_parseactions: HavingClause_p.setName('HavingClause').setParseAction(__parseInfoFunc((HavingClause)))

# [20]    GroupCondition    ::=   BuiltInCall | FunctionCall | '(' Expression ( 'AS' Var )? ')' | Var 
GroupCondition_p = Group(BuiltInCall_p | FunctionCall_p | (LPAR_p + Expression_p + Optional(AS_kw_p + Var_p) + RPAR_p) | Var_p )
class GroupCondition(SPARQLNonTerminal): pass
if do_parseactions: GroupCondition_p.setName('GroupCondition').setParseAction(__parseInfoFunc((GroupCondition)))

# [19]    GroupClause       ::=   'GROUP' 'BY' GroupCondition+ 
GroupClause_p = Group(GROUP_BY_kw_p + OneOrMore(GroupCondition_p) )
class GroupClause(SPARQLNonTerminal): pass
if do_parseactions: GroupClause_p.setName('GroupClause').setParseAction(__parseInfoFunc((GroupClause)))

# [18]    SolutionModifier          ::=   GroupClause? HavingClause? OrderClause? LimitOffsetClauses? 
SolutionModifier_p = Group(  Optional(GroupClause_p) + Optional(HavingClause_p) + Optional(OrderClause_p) + Optional(LimitOffsetClauses_p) )
class SolutionModifier(SPARQLNonTerminal): pass
if do_parseactions: SolutionModifier_p.setName('SolutionModifier').setParseAction(__parseInfoFunc((SolutionModifier)))

# [17]    WhereClause       ::=   'WHERE'? GroupGraphPattern 
WhereClause_p = Group(  Optional(WHERE_kw_p) + GroupGraphPattern_p )
class WhereClause(SPARQLNonTerminal): pass
if do_parseactions: WhereClause_p.setName('WhereClause').setParseAction(__parseInfoFunc((WhereClause)))

# [16]    SourceSelector    ::=   iri 
SourceSelector_p = Group(iri_p)
class SourceSelector(SPARQLNonTerminal): pass
if do_parseactions: SourceSelector_p.setName('SourceSelector').setParseAction(__parseInfoFunc((SourceSelector)))

# [15]    NamedGraphClause          ::=   'NAMED' SourceSelector 
NamedGraphClause_p = Group(NAMED_kw_p + SourceSelector_p )
class NamedGraphClause(SPARQLNonTerminal): pass
if do_parseactions: NamedGraphClause_p.setName('NamedGraphClause').setParseAction(__parseInfoFunc((NamedGraphClause)))

# [14]    DefaultGraphClause        ::=   SourceSelector 
DefaultGraphClause_p = Group(SourceSelector_p)
class DefaultGraphClause(SPARQLNonTerminal): pass
if do_parseactions: DefaultGraphClause_p.setName('DefaultGraphClause').setParseAction(__parseInfoFunc((DefaultGraphClause)))

# [13]    DatasetClause     ::=   'FROM' ( DefaultGraphClause | NamedGraphClause ) 
DatasetClause_p = Group(FROM_kw_p + (DefaultGraphClause_p | NamedGraphClause_p) )
class DatasetClause(SPARQLNonTerminal): pass
if do_parseactions: DatasetClause_p.setName('DatasetClause').setParseAction(__parseInfoFunc((DatasetClause)))

# [12]    AskQuery          ::=   'ASK' DatasetClause* WhereClause SolutionModifier 
AskQuery_p = Group(  ASK_kw_p + ZeroOrMore(DatasetClause_p) + WhereClause_p + SolutionModifier_p )
class AskQuery(SPARQLNonTerminal): pass
if do_parseactions: AskQuery_p.setName('AskQuery').setParseAction(__parseInfoFunc((AskQuery)))

# [11]    DescribeQuery     ::=   'DESCRIBE' ( VarOrIri+ | '*' ) DatasetClause* WhereClause? SolutionModifier 
DescribeQuery_p = Group(DESCRIBE_kw_p + (OneOrMore(VarOrIri_p) | ALL_VALUES_st_p) + ZeroOrMore(DatasetClause_p) + Optional(WhereClause_p) + SolutionModifier_p )
class DescribeQuery(SPARQLNonTerminal): pass
if do_parseactions: DescribeQuery_p.setName('DescribeQuery').setParseAction(__parseInfoFunc((DescribeQuery)))

# [10]    ConstructQuery    ::=   'CONSTRUCT' ( ConstructTemplate DatasetClause* WhereClause SolutionModifier | DatasetClause* 'WHERE' '{' TriplesTemplate? '}' SolutionModifier ) 
ConstructQuery_p = Group(CONSTRUCT_kw_p + ( (ConstructTemplate_p + ZeroOrMore(DatasetClause_p) + WhereClause_p + SolutionModifier_p) | \
                                      (ZeroOrMore(DatasetClause_p) + WHERE_kw_p + LCURL_p +  Optional(TriplesTemplate_p) + RCURL_p + SolutionModifier_p) ) )
class ConstructQuery(SPARQLNonTerminal): pass
if do_parseactions: ConstructQuery_p.setName('ConstructQuery').setParseAction(__parseInfoFunc((ConstructQuery)))

# [9]     SelectClause      ::=   'SELECT' ( 'DISTINCT' | 'REDUCED' )? ( ( Var | ( '(' Expression 'AS' Var ')' ) )+ | '*' ) 
SelectClause_p = Group(SELECT_kw_p + Optional(DISTINCT_kw_p | REDUCED_kw_p) + ( OneOrMore(Var_p | (LPAR_p + Expression_p + AS_kw_p + Var_p + RPAR_p)) | ALL_VALUES_st_p ) )
class SelectClause(SPARQLNonTerminal): pass
if do_parseactions: SelectClause_p.setName('SelectClause').setParseAction(__parseInfoFunc((SelectClause)))

# [8]     SubSelect         ::=   SelectClause WhereClause SolutionModifier ValuesClause 
SubSelect_p << Group(SelectClause_p + WhereClause_p + SolutionModifier_p + ValuesClause_p) 

# [7]     SelectQuery       ::=   SelectClause DatasetClause* WhereClause SolutionModifier 
SelectQuery_p = Group(SelectClause_p + ZeroOrMore(DatasetClause_p) + WhereClause_p + SolutionModifier_p )
class SelectQuery(SPARQLNonTerminal): pass
if do_parseactions: SelectQuery_p.setName('SelectQuery').setParseAction(__parseInfoFunc((SelectQuery)))

# [6]     PrefixDecl        ::=   'PREFIX' PNAME_NS IRIREF 
PrefixDecl_p = Group(PREFIX_kw_p + PNAME_NS_p + IRIREF_p )
class PrefixDecl(SPARQLNonTerminal): pass
if do_parseactions: PrefixDecl_p.setName('PrefixDecl').setParseAction(__parseInfoFunc((PrefixDecl)))

# [5]     BaseDecl          ::=   'BASE' IRIREF 
BaseDecl_p = Group(BASE_kw_p + IRIREF_p )
class BaseDecl(SPARQLNonTerminal): pass
if do_parseactions: BaseDecl_p.setName('BaseDecl').setParseAction(__parseInfoFunc((BaseDecl)))

# [4]     Prologue          ::=   ( BaseDecl | PrefixDecl )* 
Prologue_p << Group(ZeroOrMore(BaseDecl_p | PrefixDecl_p)) 

# [3]     UpdateUnit        ::=   Update 
UpdateUnit_p = Group(Update_p )
class UpdateUnit(SPARQLNonTerminal): pass
if do_parseactions: UpdateUnit_p.setName('UpdateUnit').setParseAction(__parseInfoFunc((UpdateUnit)))

# [2]     Query     ::=   Prologue ( SelectQuery | ConstructQuery | DescribeQuery | AskQuery ) ValuesClause 
Query_p = Group(Prologue_p + ( SelectQuery_p | ConstructQuery_p | DescribeQuery_p | AskQuery_p ) + ValuesClause_p )
class Query(SPARQLNonTerminal): pass
if do_parseactions: Query_p.setName('Query').setParseAction(__parseInfoFunc((Query)))

# [1]     QueryUnit         ::=   Query 
QueryUnit_p = Group(Query_p)
class QueryUnit(SPARQLNonTerminal): pass
if do_parseactions: QueryUnit_p.setName('QueryUnit').setParseAction(__parseInfoFunc((QueryUnit)))
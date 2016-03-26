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
    Line = ZeroOrMore(String_p | (IRIREF_p | Literal('<')) | NormalText) + Optional(Comment) + lineEnd
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
        
        self.outerList = None
        self.parent = None
        if len(args) == 2:
#             self.__dict__['name'] = args[0] 
#             self.__dict__['name'] = None
            self.__dict__['items'] = args[1] 
        else:
            assert len(args) == 1 and isinstance(args[0], str)
#             self.__dict__['name'] = None
            self.__dict__['items'] = self.__getPattern().parseString(args[0], parseAll=True)[0].items
        self.createParentPointers()
                
    def __eq__(self, other):
        '''Compares the items part of both classes for equality, recursively.
        This means that the labels are not taken into account. This is because
        the labels are a form of annotation, separate from the parse tree in terms of
        encountered production rules. Equality means that all productions are identical.'''
        return self.__class__ == other.__class__ and self.items == other.items
    
#     def __getattr__(self, label):
#         '''Retrieves the unique element corresponding to the label (non-recursive). Raises an exception if zero, or more than one values exist.'''
#         if label in self.getLabels():
#             values = self.getValuesForLabel(label)
#             assert len(values) == 1
#             return values[0] 
#         else:
#             raise AttributeError('Unknown label: {}'.format(label))
#         
#     def __setattr__(self, label, value):
#         '''Raises exception when trying to set attributes directly.Elements are to be changed using "updateWith()".'''
#         raise AttributeError('Direct setting of attributes not allowed. Try updateWith() instead.')
    
    def __repr__(self):
        return self.__class__.__name__ + '("' + str(self) + '")'
   
#     def __isLabelConsistent(self):
#         '''Checks if for labels are only not None for pairs [label, value] where value is a ParseInfo instance, and in those cases label must be equal to value.name.
#         This is for internal use only.'''
#         return all([i[0] == i[1].name if isinstance(i[1], ParseInfo) else i[0] == None if isinstance(i[1], str) else False for i in self.getItems()]) and \
#                 all([i[1].__isLabelConsistent() if isinstance(i[1], ParseInfo) else i[0] == None for i in self.getItems()])

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
        if self.getName() or not labeledOnly:
                result.append(self)
        result.extend(flattenList(self.getItems()))
        return result  
    
    def createParentPointers(self):
        for i in self.getItems():
            if isinstance(i[1], ParseInfo):
                i[1].parent = self
    
    def searchElements(self, *, label=None, element_type = None, value = None, labeledOnly=False):
        '''Returns a list of all elements with the specified search pattern. If labeledOnly is True,
        only elements with label not None are considered for inclusion. Otherwise (the default case) all elements are considered.
        Keyword arguments label, element_type, value are used as a wildcard if None. All must be matched for an element to be included in the result.'''
        
        result = []
        
        for e in [self] + self.__getElements(labeledOnly=labeledOnly):
#             print('DEBUG: e.name =', e.getName())

            if label and label != e.getName():
                continue
            if element_type and element_type != e.__class__:
                continue
            if value:
                try:
                    e1 = e.pattern.parseString(value)[0]
                    if e != e1:
                        continue
                except ParseException:
                    continue
            result.append(e)
        return result    
        
    def copy(self):
        '''Returns a deep copy of itself.'''
        result = globals()[self.__class__.__name__](self.getName(), self.__copyItems())
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
    
    def check(self, *, report = False, render=False, dump=False):
        '''Runs various checks. Returns True if all checks pass, else False. Optionally prints a report with the check results, renders, and/or dumps itself.'''
        if report:
            print('{} is{}internally label-consistent'.format(self, ' ' if self.__isLabelConsistent() else ' not '))
            print('{} renders a{}expression ({})'.format(self, ' valid ' if self.yieldsValidExpression() else 'n invalid ', self.__str__()))
            print('{} is a{}valid parse object'.format(self, ' ' if self.isValid() else ' not '))
        if render:
            print('--rendering:')
            self.render()
        if dump:
            print('--dump:')
            print(self.dump())
        return self.__isLabelConsistent() and self.yieldsValidExpression() and self.isValid()

    def getName(self):
        '''Returns name attribute (non-recursive).'''
        try:
            return self.outerList[0]
        except TypeError:
            return None
    
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
    
    def getChildren(self):
        '''Returns a list of all its child elements.'''
        return [i[1] for i in self.getItems() if isinstance(i[1], ParseInfo)]
    
    def getParent(self):
        '''Returns a list of its parent element, which is the first element encountered when going up to top, which can be any element in the parse tree.
        It must be given to provide a context for the search, and will normally correspond to the main expression parsed.'''
        return self.parent
#         for i in top.searchElements():
#             if self in i.getChildren():
#                 return i
#         return None
    
    def getAncestors(self, top):
        '''Returns the list of parent nodes, starting with the direct parent and ending with top.'''
        result = []
        parent = self.getParent(top)
        while parent:
            result.append(parent)
            parent = parent.getParent(top)
        return result
    
    def isBranch(self):
        '''Checks whether the node branches.'''
        return len(self.getItems()) > 1
            
    def isAtom(self):
        '''Test whether the node has no ParseInfo subnode, but contains a string.'''
        return len(self.getItems()) == 1 and isinstance(self.items[0][1], str)
    
    def descend(self):
        '''Descends until either an atom or a branch node is encountered; returns that node.'''
        result = self
        while not result.isAtom() and not result.isBranch():
#             if isinstance(result, str): print()
            result = result.items[0][1]
        return result
        
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
       
        result += indent + ('> '+ self.getName() + ':\n' + indent if self.getName() else '') + '[' + self.__class__.__name__ + '] ' + '/' + self.__str__() + '/' + '\n'
        result += dumpItems(self.items, indent, step)
        
        return result

#     def __str__(self):
#         '''Generates the string corresponding to the object. Except for whitespace variations, 
#         this is identical to the string that was used to create the object.'''
#         sep = ' '
# #         def renderList(l):
# #             resultList = []
# #             for i in l:
# #                 if isinstance(i, str):
# #                     resultList.append(i)
# #                     continue
# #                 if isinstance(i, ParseInfo):
# #                     resultList.append(i.__str__())
# #                     continue
# #                 if isinstance(i, list):
# #                     resultList.append(renderList(i))
# #             return sep.join(resultList)
#         result = []
#         for t in self.items:
#             if isinstance(t[1], str):
#                 result.append(t[1]) 
# #             elif isinstance(t[1], list):
# #                 result.append(renderList(t[1]))
#             else:
#                 assert isinstance(t[1], ParseInfo), type(t[1])
#                 result.append(t[1].__str__())
#         return sep.join([r for r in result if r != ''])
    
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
    
    
def parseInfoFunc(cls):
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
                i = [None, t]
                result.append(i)
            elif isinstance(t, ParseInfo):
#                 t.createParentPointers()
                i = [valuedict.get(id(t)), t]
                t.outerList = i
                t.__dict__['name'] = valuedict.get(id(t))
                result.append(i)
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

def separatedList(pattern, sep=','):
    '''Similar to a delimited list of instances from a ParseInfo subclass, but includes the separator in its ParseResults. Returns a 
    ParseResults object containing a simple list of matched tokens separated by the separator.'''
    
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
            result.append(sep)
            result.append(p)
        return result

    
    result = delimitedList(pattern, sep)
    if do_parseactions:
        result.setParseAction(makeList)
    return result

      
class Terminal_(ParseInfo):
    def __str__(self):
        return ''.join([t[1] for t in self.items])
            
            
class NonTerminal_(ParseInfo):
    def __str__(self):
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


class Keyword_(ParseInfo):
    def __str__(self):
        return ' '.join([t[1] for t in self.items])


class Operator_(ParseInfo):
    def __str__(self):
        return self.items[0][1]



# Special tokens
ALL_VALUES_st_p = Literal('*')
class ALL_VALUES_st(Keyword_):
    pass
    def __str__(self):
        return '*'
if do_parseactions: ALL_VALUES_st_p.setName('ALL_VALUES_st').setParseAction(parseInfoFunc((ALL_VALUES_st)))

#
# Brackets and interpunction
#

LPAR_p, RPAR_p, LBRACK_p, RBRACK_p, LCURL_p, RCURL_p, SEMICOL_p, COMMA_p, PERIOD_p = map(Literal, '()[]{};,.')

#
# Operators
#

NOT_op_p = Literal('!')
class NOT_op(Operator_): pass
if do_parseactions: NOT_op_p.setName('NOT_op').setParseAction(parseInfoFunc((NOT_op)))

PLUS_op_p = Literal('+')
class PLUS_op(Operator_): pass
if do_parseactions: PLUS_op_p.setName('PLUS_op').setParseAction(parseInfoFunc((PLUS_op)))

MINUS_op_p = Literal('-')
class MINUS_op(Operator_): pass
if do_parseactions: MINUS_op_p.setName('MINUS_op').setParseAction(parseInfoFunc((MINUS_op)))

TIMES_op_p = Literal('*')
class TIMES_op(Operator_): pass
if do_parseactions: TIMES_op_p.setName('TIMES_op').setParseAction(parseInfoFunc((TIMES_op)))

DIV_op_p = Literal('/')
class DIV_op(Operator_): pass
if do_parseactions: DIV_op_p.setName('DIV_op').setParseAction(parseInfoFunc((DIV_op)))

EQ_op_p = Literal('=') 
class EQ_op(Operator_): pass
if do_parseactions: EQ_op_p.setName('EQ_op').setParseAction(parseInfoFunc((EQ_op)))

NE_op_p = Literal('!=') 
class NE_op(Operator_): pass
if do_parseactions: NE_op_p.setName('NE_op').setParseAction(parseInfoFunc((NE_op)))

GT_op_p = Literal('>') 
class GT_op(Operator_): pass
if do_parseactions: GT_op_p.setName('GT_op').setParseAction(parseInfoFunc((GT_op)))

LT_op_p = Literal('<') 
class LT_op(Operator_): pass
if do_parseactions: LT_op_p.setName('LT_op').setParseAction(parseInfoFunc((LT_op)))

GE_op_p = Literal('>=') 
class GE_op(Operator_): pass
if do_parseactions: GE_op_p.setName('GE_op').setParseAction(parseInfoFunc((GE_op)))

LE_op_p = Literal('<=') 
class LE_op(Operator_): pass
if do_parseactions: LE_op_p.setName('LE_op').setParseAction(parseInfoFunc((LE_op)))

AND_op_p = Literal('&&')
class AND_op(Operator_): pass
if do_parseactions: AND_op_p.setName('AND_op').setParseAction(parseInfoFunc((AND_op)))
  
OR_op_p = Literal('||')
class OR_op(Operator_): pass
if do_parseactions: OR_op_p.setName('OR_op').setParseAction(parseInfoFunc((OR_op)))

INVERSE_op_p = Literal('^')
class INVERSE_op(Operator_): pass
if do_parseactions: INVERSE_op_p.setName('INVERSE_op').setParseAction(parseInfoFunc((INVERSE_op)))


#
# Keywords
#

ALL_VALUES_kw_p = Literal('*')
class ALL_VALUES_kw(Keyword_): pass
if do_parseactions: ALL_VALUES_kw_p.setName('ALL_VALUES_kw').setParseAction(parseInfoFunc((ALL_VALUES_kw)))

TYPE_kw_p = Keyword('a')
class TYPE_kw(Keyword_): pass
if do_parseactions: TYPE_kw_p.setName('TYPE_kw').setParseAction(parseInfoFunc((TYPE_kw)))

DISTINCT_kw_p = CaselessKeyword('DISTINCT')
class DISTINCT_kw(Keyword_): pass
if do_parseactions: DISTINCT_kw_p.setName('DISTINCT_kw').setParseAction(parseInfoFunc((DISTINCT_kw)))

COUNT_kw_p = CaselessKeyword('COUNT')
class COUNT_kw(Keyword_): pass
if do_parseactions: COUNT_kw_p.setName('COUNT_kw').setParseAction(parseInfoFunc((COUNT_kw)))

SUM_kw_p = CaselessKeyword('SUM')
class SUM_kw(Keyword_): pass
if do_parseactions: SUM_kw_p.setName('SUM_kw').setParseAction(parseInfoFunc((SUM_kw)))

MIN_kw_p = CaselessKeyword('MIN') 
class MIN_kw(Keyword_): pass
if do_parseactions: MIN_kw_p.setName('MIN_kw').setParseAction(parseInfoFunc((MIN_kw)))

MAX_kw_p = CaselessKeyword('MAX') 
class MAX_kw(Keyword_): pass
if do_parseactions: MAX_kw_p.setName('MAX_kw').setParseAction(parseInfoFunc((MAX_kw)))

AVG_kw_p = CaselessKeyword('AVG') 
class AVG_kw(Keyword_): pass
if do_parseactions: AVG_kw_p.setName('AVG_kw').setParseAction(parseInfoFunc((AVG_kw)))

SAMPLE_kw_p = CaselessKeyword('SAMPLE') 
class SAMPLE_kw(Keyword_): pass
if do_parseactions: SAMPLE_kw_p.setName('SAMPLE_kw').setParseAction(parseInfoFunc((SAMPLE_kw)))

GROUP_CONCAT_kw_p = CaselessKeyword('GROUP_CONCAT') 
class GROUP_CONCAT_kw(Keyword_): pass
if do_parseactions: GROUP_CONCAT_kw_p.setName('GROUP_CONCAT_kw').setParseAction(parseInfoFunc((GROUP_CONCAT_kw)))

SEPARATOR_kw_p = CaselessKeyword('SEPARATOR')
class SEPARATOR_kw(Keyword_): pass
if do_parseactions: SEPARATOR_kw_p.setName('SEPARATOR_kw').setParseAction(parseInfoFunc((SEPARATOR_kw)))

NOT_kw_p = CaselessKeyword('NOT') + NotAny(CaselessKeyword('EXISTS') | CaselessKeyword('IN'))
class NOT_kw(Keyword_): pass
if do_parseactions: NOT_kw_p.setName('NOT_kw').setParseAction(parseInfoFunc((NOT_kw)))

EXISTS_kw_p = CaselessKeyword('EXISTS')
class EXISTS_kw(Keyword_): pass
if do_parseactions: EXISTS_kw_p.setName('EXISTS_kw').setParseAction(parseInfoFunc((EXISTS_kw)))

NOT_EXISTS_kw_p = CaselessKeyword('NOT') + CaselessKeyword('EXISTS')
class NOT_EXISTS_kw(Keyword_): pass
if do_parseactions: NOT_EXISTS_kw_p.setName('NOT_EXISTS_kw').setParseAction(parseInfoFunc((NOT_EXISTS_kw)))

REPLACE_kw_p = CaselessKeyword('REPLACE')
class REPLACE_kw(Keyword_): pass
if do_parseactions: REPLACE_kw_p.setName('REPLACE_kw').setParseAction(parseInfoFunc((REPLACE_kw)))

SUBSTR_kw_p = CaselessKeyword('SUBSTR')
class SUBSTR_kw(Keyword_): pass
if do_parseactions: SUBSTR_kw_p.setName('SUBSTR_kw').setParseAction(parseInfoFunc((SUBSTR_kw)))

REGEX_kw_p = CaselessKeyword('REGEX')
class REGEX_kw(Keyword_): pass
if do_parseactions: REGEX_kw_p.setName('REGEX_kw').setParseAction(parseInfoFunc((REGEX_kw)))

STR_kw_p = CaselessKeyword('STR') 
class STR_kw(Keyword_): pass
if do_parseactions: STR_kw_p.setName('STR_kw').setParseAction(parseInfoFunc((STR_kw)))

LANG_kw_p = CaselessKeyword('LANG') 
class LANG_kw(Keyword_): pass
if do_parseactions: LANG_kw_p.setName('LANG_kw').setParseAction(parseInfoFunc((LANG_kw)))

LANGMATCHES_kw_p = CaselessKeyword('LANGMATCHES') 
class LANGMATCHES_kw(Keyword_): pass
if do_parseactions: LANGMATCHES_kw_p.setName('LANGMATCHES_kw').setParseAction(parseInfoFunc((LANGMATCHES_kw)))

DATATYPE_kw_p = CaselessKeyword('DATATYPE') 
class DATATYPE_kw(Keyword_): pass
if do_parseactions: DATATYPE_kw_p.setName('DATATYPE_kw').setParseAction(parseInfoFunc((DATATYPE_kw)))

BOUND_kw_p = CaselessKeyword('BOUND') 
class BOUND_kw(Keyword_): pass
if do_parseactions: BOUND_kw_p.setName('BOUND_kw').setParseAction(parseInfoFunc((BOUND_kw)))

IRI_kw_p = CaselessKeyword('IRI') 
class IRI_kw(Keyword_): pass
if do_parseactions: IRI_kw_p.setName('IRI_kw').setParseAction(parseInfoFunc((IRI_kw)))

URI_kw_p = CaselessKeyword('URI') 
class URI_kw(Keyword_): pass
if do_parseactions: URI_kw_p.setName('URI_kw').setParseAction(parseInfoFunc((URI_kw)))

BNODE_kw_p = CaselessKeyword('BNODE') 
class BNODE_kw(Keyword_): pass
if do_parseactions: BNODE_kw_p.setName('BNODE_kw').setParseAction(parseInfoFunc((BNODE_kw)))

RAND_kw_p = CaselessKeyword('RAND') 
class RAND_kw(Keyword_): pass
if do_parseactions: RAND_kw_p.setName('RAND_kw').setParseAction(parseInfoFunc((RAND_kw)))

ABS_kw_p = CaselessKeyword('ABS') 
class ABS_kw(Keyword_): pass
if do_parseactions: ABS_kw_p.setName('ABS_kw').setParseAction(parseInfoFunc((ABS_kw)))

CEIL_kw_p = CaselessKeyword('CEIL') 
class CEIL_kw(Keyword_): pass
if do_parseactions: CEIL_kw_p.setName('CEIL_kw').setParseAction(parseInfoFunc((CEIL_kw)))

FLOOR_kw_p = CaselessKeyword('FLOOR') 
class FLOOR_kw(Keyword_): pass
if do_parseactions: FLOOR_kw_p.setName('FLOOR_kw').setParseAction(parseInfoFunc((FLOOR_kw)))

ROUND_kw_p = CaselessKeyword('ROUND') 
class ROUND_kw(Keyword_): pass
if do_parseactions: ROUND_kw_p.setName('ROUND_kw').setParseAction(parseInfoFunc((ROUND_kw)))

CONCAT_kw_p = CaselessKeyword('CONCAT') 
class CONCAT_kw(Keyword_): pass
if do_parseactions: CONCAT_kw_p.setName('CONCAT_kw').setParseAction(parseInfoFunc((CONCAT_kw)))

STRLEN_kw_p = CaselessKeyword('STRLEN') 
class STRLEN_kw(Keyword_): pass
if do_parseactions: STRLEN_kw_p.setName('STRLEN_kw').setParseAction(parseInfoFunc((STRLEN_kw)))

UCASE_kw_p = CaselessKeyword('UCASE') 
class UCASE_kw(Keyword_): pass
if do_parseactions: UCASE_kw_p.setName('UCASE_kw').setParseAction(parseInfoFunc((UCASE_kw)))

LCASE_kw_p = CaselessKeyword('LCASE') 
class LCASE_kw(Keyword_): pass
if do_parseactions: LCASE_kw_p.setName('LCASE_kw').setParseAction(parseInfoFunc((LCASE_kw)))

ENCODE_FOR_URI_kw_p = CaselessKeyword('ENCODE_FOR_URI') 
class ENCODE_FOR_URI_kw(Keyword_): pass
if do_parseactions: ENCODE_FOR_URI_kw_p.setName('ENCODE_FOR_URI_kw').setParseAction(parseInfoFunc((ENCODE_FOR_URI_kw)))

CONTAINS_kw_p = CaselessKeyword('CONTAINS') 
class CONTAINS_kw(Keyword_): pass
if do_parseactions: CONTAINS_kw_p.setName('CONTAINS_kw').setParseAction(parseInfoFunc((CONTAINS_kw)))

STRSTARTS_kw_p = CaselessKeyword('STRSTARTS') 
class STRSTARTS_kw(Keyword_): pass
if do_parseactions: STRSTARTS_kw_p.setName('STRSTARTS_kw').setParseAction(parseInfoFunc((STRSTARTS_kw)))

STRENDS_kw_p = CaselessKeyword('STRENDS') 
class STRENDS_kw(Keyword_): pass
if do_parseactions: STRENDS_kw_p.setName('STRENDS_kw').setParseAction(parseInfoFunc((STRENDS_kw)))

STRBEFORE_kw_p = CaselessKeyword('STRBEFORE') 
class STRBEFORE_kw(Keyword_): pass
if do_parseactions: STRBEFORE_kw_p.setName('STRBEFORE_kw').setParseAction(parseInfoFunc((STRBEFORE_kw)))

STRAFTER_kw_p = CaselessKeyword('STRAFTER') 
class STRAFTER_kw(Keyword_): pass
if do_parseactions: STRAFTER_kw_p.setName('STRAFTER_kw').setParseAction(parseInfoFunc((STRAFTER_kw)))

YEAR_kw_p = CaselessKeyword('YEAR') 
class YEAR_kw(Keyword_): pass
if do_parseactions: YEAR_kw_p.setName('YEAR_kw').setParseAction(parseInfoFunc((YEAR_kw)))

MONTH_kw_p = CaselessKeyword('MONTH') 
class MONTH_kw(Keyword_): pass
if do_parseactions: MONTH_kw_p.setName('MONTH_kw').setParseAction(parseInfoFunc((MONTH_kw)))

DAY_kw_p = CaselessKeyword('DAY') 
class DAY_kw(Keyword_): pass
if do_parseactions: DAY_kw_p.setName('DAY_kw').setParseAction(parseInfoFunc((DAY_kw)))

HOURS_kw_p = CaselessKeyword('HOURS') 
class HOURS_kw(Keyword_): pass
if do_parseactions: HOURS_kw_p.setName('HOURS_kw').setParseAction(parseInfoFunc((HOURS_kw)))

MINUTES_kw_p = CaselessKeyword('MINUTES') 
class MINUTES_kw(Keyword_): pass
if do_parseactions: MINUTES_kw_p.setName('MINUTES_kw').setParseAction(parseInfoFunc((MINUTES_kw)))

SECONDS_kw_p = CaselessKeyword('SECONDS') 
class SECONDS_kw(Keyword_): pass
if do_parseactions: SECONDS_kw_p.setName('SECONDS_kw').setParseAction(parseInfoFunc((SECONDS_kw)))

TIMEZONE_kw_p = CaselessKeyword('TIMEZONE') 
class TIMEZONE_kw(Keyword_): pass
if do_parseactions: TIMEZONE_kw_p.setName('TIMEZONE_kw').setParseAction(parseInfoFunc((TIMEZONE_kw)))

TZ_kw_p = CaselessKeyword('TZ') 
class TZ_kw(Keyword_): pass
if do_parseactions: TZ_kw_p.setName('TZ_kw').setParseAction(parseInfoFunc((TZ_kw)))

NOW_kw_p = CaselessKeyword('NOW') 
class NOW_kw(Keyword_): pass
if do_parseactions: NOW_kw_p.setName('NOW_kw').setParseAction(parseInfoFunc((NOW_kw)))

UUID_kw_p = CaselessKeyword('UUID') 
class UUID_kw(Keyword_): pass
if do_parseactions: UUID_kw_p.setName('UUID_kw').setParseAction(parseInfoFunc((UUID_kw)))

STRUUID_kw_p = CaselessKeyword('STRUUID') 
class STRUUID_kw(Keyword_): pass
if do_parseactions: STRUUID_kw_p.setName('STRUUID_kw').setParseAction(parseInfoFunc((STRUUID_kw)))

MD5_kw_p = CaselessKeyword('MD5') 
class MD5_kw(Keyword_): pass
if do_parseactions: MD5_kw_p.setParseAction(parseInfoFunc(MD5_kw))

SHA1_kw_p = CaselessKeyword('SHA1') 
class SHA1_kw(Keyword_): pass
if do_parseactions: SHA1_kw_p.setParseAction(parseInfoFunc(SHA1_kw))

SHA256_kw_p = CaselessKeyword('SHA256') 
class SHA256_kw(Keyword_): pass
if do_parseactions: SHA256_kw_p.setParseAction(parseInfoFunc(SHA256_kw))

SHA384_kw_p = CaselessKeyword('SHA384') 
class SHA384_kw(Keyword_): pass
if do_parseactions: SHA384_kw_p.setParseAction(parseInfoFunc(SHA384_kw))

SHA512_kw_p = CaselessKeyword('SHA512') 
class SHA512_kw(Keyword_): pass
if do_parseactions: SHA512_kw_p.setParseAction(parseInfoFunc(SHA512_kw))

COALESCE_kw_p = CaselessKeyword('COALESCE') 
class COALESCE_kw(Keyword_): pass
if do_parseactions: COALESCE_kw_p.setName('COALESCE_kw').setParseAction(parseInfoFunc((COALESCE_kw)))

IF_kw_p = CaselessKeyword('IF') 
class IF_kw(Keyword_): pass
if do_parseactions: IF_kw_p.setName('IF_kw').setParseAction(parseInfoFunc((IF_kw)))

STRLANG_kw_p = CaselessKeyword('STRLANG') 
class STRLANG_kw(Keyword_): pass
if do_parseactions: STRLANG_kw_p.setName('STRLANG_kw').setParseAction(parseInfoFunc((STRLANG_kw)))

STRDT_kw_p = CaselessKeyword('STRDT') 
class STRDT_kw(Keyword_): pass
if do_parseactions: STRDT_kw_p.setName('STRDT_kw').setParseAction(parseInfoFunc((STRDT_kw)))

sameTerm_kw_p = CaselessKeyword('sameTerm') 
class sameTerm_kw(Keyword_): pass
if do_parseactions: sameTerm_kw_p.setName('sameTerm_kw').setParseAction(parseInfoFunc((sameTerm_kw)))

isIRI_kw_p = CaselessKeyword('isIRI') 
class isIRI_kw(Keyword_): pass
if do_parseactions: isIRI_kw_p.setName('isIRI_kw').setParseAction(parseInfoFunc((isIRI_kw)))

isURI_kw_p = CaselessKeyword('isURI') 
class isURI_kw(Keyword_): pass
if do_parseactions: isURI_kw_p.setName('isURI_kw').setParseAction(parseInfoFunc((isURI_kw)))

isBLANK_kw_p = CaselessKeyword('isBLANK') 
class isBLANK_kw(Keyword_): pass
if do_parseactions: isBLANK_kw_p.setName('isBLANK_kw').setParseAction(parseInfoFunc((isBLANK_kw)))

isLITERAL_kw_p = CaselessKeyword('isLITERAL') 
class isLITERAL_kw(Keyword_): pass
if do_parseactions: isLITERAL_kw_p.setName('isLITERAL_kw').setParseAction(parseInfoFunc((isLITERAL_kw)))

isNUMERIC_kw_p = CaselessKeyword('isNUMERIC') 
class isNUMERIC_kw(Keyword_): pass
if do_parseactions: isNUMERIC_kw_p.setName('isNUMERIC_kw').setParseAction(parseInfoFunc((isNUMERIC_kw)))

IN_kw_p = CaselessKeyword('IN') 
class IN_kw(Keyword_): pass
if do_parseactions: IN_kw_p.setName('IN_kw').setParseAction(parseInfoFunc((IN_kw)))

NOT_IN_kw_p = CaselessKeyword('NOT') + CaselessKeyword('IN')
class NOT_IN_kw(Keyword_): pass
if do_parseactions: NOT_IN_kw_p.setName('NOT_IN_kw').setParseAction(parseInfoFunc((NOT_IN_kw)))

FILTER_kw_p = CaselessKeyword('FILTER')
class FILTER_kw(Keyword_): pass
if do_parseactions: FILTER_kw_p.setName('FILTER_kw').setParseAction(parseInfoFunc((FILTER_kw)))

UNION_kw_p = CaselessKeyword('UNION')
class UNION_kw(Keyword_): pass
if do_parseactions: UNION_kw_p.setName('UNION_kw').setParseAction(parseInfoFunc((UNION_kw)))

MINUS_kw_p = CaselessKeyword('MINUS')
class MINUS_kw(Keyword_): pass
if do_parseactions: MINUS_kw_p.setName('MINUS_kw').setParseAction(parseInfoFunc((MINUS_kw)))

UNDEF_kw_p = CaselessKeyword('UNDEF')
class UNDEF_kw(Keyword_): pass
if do_parseactions: UNDEF_kw_p.setName('UNDEF_kw').setParseAction(parseInfoFunc((UNDEF_kw)))

VALUES_kw_p = CaselessKeyword('VALUES')
class VALUES_kw(Keyword_): pass
if do_parseactions: VALUES_kw_p.setName('VALUES_kw').setParseAction(parseInfoFunc((VALUES_kw)))

BIND_kw_p = CaselessKeyword('BIND')
class BIND_kw(Keyword_): pass
if do_parseactions: BIND_kw_p.setName('BIND_kw').setParseAction(parseInfoFunc((BIND_kw)))

AS_kw_p = CaselessKeyword('AS')
class AS_kw(Keyword_): pass
if do_parseactions: AS_kw_p.setName('AS_kw').setParseAction(parseInfoFunc((AS_kw)))

SERVICE_kw_p = CaselessKeyword('SERVICE')
class SERVICE_kw(Keyword_): pass
if do_parseactions: SERVICE_kw_p.setName('SERVICE_kw').setParseAction(parseInfoFunc((SERVICE_kw)))

SILENT_kw_p = CaselessKeyword('SILENT')
class SILENT_kw(Keyword_): pass
if do_parseactions: SILENT_kw_p.setName('SILENT_kw').setParseAction(parseInfoFunc((SILENT_kw)))

GRAPH_kw_p = CaselessKeyword('GRAPH')
class GRAPH_kw(Keyword_): pass
if do_parseactions: GRAPH_kw_p.setName('GRAPH_kw').setParseAction(parseInfoFunc((GRAPH_kw)))

OPTIONAL_kw_p = CaselessKeyword('OPTIONAL')
class OPTIONAL_kw(Keyword_): pass
if do_parseactions: OPTIONAL_kw_p.setName('OPTIONAL_kw').setParseAction(parseInfoFunc((OPTIONAL_kw)))

DEFAULT_kw_p = CaselessKeyword('DEFAULT')
class DEFAULT_kw(Keyword_): pass
if do_parseactions: DEFAULT_kw_p.setName('DEFAULT_kw').setParseAction(parseInfoFunc((DEFAULT_kw)))

NAMED_kw_p = CaselessKeyword('NAMED')
class NAMED_kw(Keyword_): pass
if do_parseactions: NAMED_kw_p.setName('NAMED_kw').setParseAction(parseInfoFunc((NAMED_kw)))

ALL_kw_p = CaselessKeyword('ALL')
class ALL_kw(Keyword_): pass
if do_parseactions: ALL_kw_p.setName('ALL_kw').setParseAction(parseInfoFunc((ALL_kw)))

USING_kw_p = CaselessKeyword('USING')
class USING_kw(Keyword_): pass
if do_parseactions: USING_kw_p.setName('USING_kw').setParseAction(parseInfoFunc((USING_kw)))

INSERT_kw_p = CaselessKeyword('INSERT')
class INSERT_kw(Keyword_): pass
if do_parseactions: INSERT_kw_p.setName('INSERT_kw').setParseAction(parseInfoFunc((INSERT_kw)))

DELETE_kw_p = CaselessKeyword('DELETE')
class DELETE_kw(Keyword_): pass
if do_parseactions: DELETE_kw_p.setName('DELETE_kw').setParseAction(parseInfoFunc((DELETE_kw)))

WITH_kw_p = CaselessKeyword('WITH')
class WITH_kw(Keyword_): pass
if do_parseactions: WITH_kw_p.setName('WITH_kw').setParseAction(parseInfoFunc((WITH_kw)))

WHERE_kw_p = CaselessKeyword('WHERE')
class WHERE_kw(Keyword_): pass
if do_parseactions: WHERE_kw_p.setName('WHERE_kw').setParseAction(parseInfoFunc((WHERE_kw)))

DELETE_WHERE_kw_p = CaselessKeyword('DELETE') + CaselessKeyword('WHERE')
class DELETE_WHERE_kw(Keyword_): pass
if do_parseactions: DELETE_WHERE_kw_p.setName('DELETE_WHERE_kw').setParseAction(parseInfoFunc((DELETE_WHERE_kw)))

DELETE_DATA_kw_p = CaselessKeyword('DELETE') + CaselessKeyword('DATA')
class DELETE_DATA_kw(Keyword_): pass
if do_parseactions: DELETE_DATA_kw_p.setName('DELETE_DATA_kw').setParseAction(parseInfoFunc((DELETE_DATA_kw)))

INSERT_DATA_kw_p = CaselessKeyword('INSERT') + CaselessKeyword('DATA')
class INSERT_DATA_kw(Keyword_): pass
if do_parseactions: INSERT_DATA_kw_p.setName('INSERT_DATA_kw').setParseAction(parseInfoFunc((INSERT_DATA_kw)))

COPY_kw_p = CaselessKeyword('COPY')
class COPY_kw(Keyword_): pass
if do_parseactions: COPY_kw_p.setName('COPY_kw').setParseAction(parseInfoFunc((COPY_kw)))

MOVE_kw_p = CaselessKeyword('MOVE')
class MOVE_kw(Keyword_): pass
if do_parseactions: MOVE_kw_p.setName('MOVE_kw').setParseAction(parseInfoFunc((MOVE_kw)))

ADD_kw_p = CaselessKeyword('ADD')
class ADD_kw(Keyword_): pass
if do_parseactions: ADD_kw_p.setName('ADD_kw').setParseAction(parseInfoFunc((ADD_kw)))

CREATE_kw_p = CaselessKeyword('CREATE')
class CREATE_kw(Keyword_): pass
if do_parseactions: CREATE_kw_p.setName('CREATE_kw').setParseAction(parseInfoFunc((CREATE_kw)))

DROP_kw_p = CaselessKeyword('DROP')
class DROP_kw(Keyword_): pass
if do_parseactions: DROP_kw_p.setName('DROP_kw').setParseAction(parseInfoFunc((DROP_kw)))

CLEAR_kw_p = CaselessKeyword('CLEAR')
class CLEAR_kw(Keyword_): pass
if do_parseactions: CLEAR_kw_p.setName('CLEAR_kw').setParseAction(parseInfoFunc((CLEAR_kw)))

LOAD_kw_p = CaselessKeyword('LOAD')
class LOAD_kw(Keyword_): pass
if do_parseactions: LOAD_kw_p.setName('LOAD_kw').setParseAction(parseInfoFunc((LOAD_kw)))

TO_kw_p = CaselessKeyword('TO')
class TO_kw(Keyword_): pass
if do_parseactions: TO_kw_p.setName('TO_kw').setParseAction(parseInfoFunc((TO_kw)))

INTO_kw_p = CaselessKeyword('INTO')
class INTO_kw(Keyword_): pass
if do_parseactions: INTO_kw_p.setName('INTO_kw').setParseAction(parseInfoFunc((INTO_kw)))

OFFSET_kw_p = CaselessKeyword('OFFSET')
class OFFSET_kw(Keyword_): pass
if do_parseactions: OFFSET_kw_p.setName('OFFSET_kw').setParseAction(parseInfoFunc((OFFSET_kw)))

LIMIT_kw_p = CaselessKeyword('LIMIT')
class LIMIT_kw(Keyword_): pass
if do_parseactions: LIMIT_kw_p.setName('LIMIT_kw').setParseAction(parseInfoFunc((LIMIT_kw)))

ASC_kw_p = CaselessKeyword('ASC')
class ASC_kw(Keyword_): pass
if do_parseactions: ASC_kw_p.setName('ASC_kw').setParseAction(parseInfoFunc((ASC_kw)))

DESC_kw_p = CaselessKeyword('DESC')
class DESC_kw(Keyword_): pass
if do_parseactions: DESC_kw_p.setName('DESC_kw').setParseAction(parseInfoFunc((DESC_kw)))

ORDER_BY_kw_p = CaselessKeyword('ORDER') + CaselessKeyword('BY')
class ORDER_BY_kw(Keyword_): pass
if do_parseactions: ORDER_BY_kw_p.setName('ORDER_BY_kw').setParseAction(parseInfoFunc((ORDER_BY_kw)))

HAVING_kw_p = CaselessKeyword('HAVING') 
class HAVING_kw(Keyword_): pass
if do_parseactions: HAVING_kw_p.setName('HAVING_kw').setParseAction(parseInfoFunc((HAVING_kw)))

GROUP_BY_kw_p = CaselessKeyword('GROUP') + CaselessKeyword('BY') 
class GROUP_BY_kw(Keyword_): pass
if do_parseactions: GROUP_BY_kw_p.setName('GROUP_BY_kw').setParseAction(parseInfoFunc((GROUP_BY_kw)))

FROM_kw_p = CaselessKeyword('FROM')
class FROM_kw(Keyword_): pass
if do_parseactions: FROM_kw_p.setName('FROM_kw').setParseAction(parseInfoFunc((FROM_kw)))

ASK_kw_p = CaselessKeyword('ASK')
class ASK_kw(Keyword_): pass
if do_parseactions: ASK_kw_p.setName('ASK_kw').setParseAction(parseInfoFunc((ASK_kw)))

DESCRIBE_kw_p = CaselessKeyword('DESCRIBE')
class DESCRIBE_kw(Keyword_): pass
if do_parseactions: DESCRIBE_kw_p.setName('DESCRIBE_kw').setParseAction(parseInfoFunc((DESCRIBE_kw)))

CONSTRUCT_kw_p = CaselessKeyword('CONSTRUCT')
class CONSTRUCT_kw(Keyword_): pass
if do_parseactions: CONSTRUCT_kw_p.setName('CONSTRUCT_kw').setParseAction(parseInfoFunc((CONSTRUCT_kw)))

SELECT_kw_p = CaselessKeyword('SELECT')
class SELECT_kw(Keyword_): pass
if do_parseactions: SELECT_kw_p.setName('SELECT_kw').setParseAction(parseInfoFunc((SELECT_kw)))

REDUCED_kw_p = CaselessKeyword('REDUCED')
class REDUCED_kw(Keyword_): pass
if do_parseactions: REDUCED_kw_p.setName('REDUCED_kw').setParseAction(parseInfoFunc((REDUCED_kw)))

PREFIX_kw_p = CaselessKeyword('PREFIX')
class PREFIX_kw(Keyword_): pass
if do_parseactions: PREFIX_kw_p.setName('PREFIX_kw').setParseAction(parseInfoFunc((PREFIX_kw)))

BASE_kw_p = CaselessKeyword('BASE')
class BASE_kw(Keyword_): pass
if do_parseactions: BASE_kw_p.setName('BASE_kw').setParseAction(parseInfoFunc((BASE_kw)))


# 
# Parsers and classes for terminals
#

# [173]   PN_LOCAL_ESC      ::=   '\' ( '_' | '~' | '.' | '-' | '!' | '$' | '&' | "'" | '(' | ')' | '*' | '+' | ',' | ';' | '=' | '/' | '?' | '#' | '@' | '%' ) 
PN_LOCAL_ESC_e = r'\\[_~.\-!$&\'()*+,;=/?#@%]'
PN_LOCAL_ESC_p = Regex(PN_LOCAL_ESC_e)
class PN_LOCAL_ESC(Terminal_): pass
if do_parseactions: PN_LOCAL_ESC_p.setName('PN_LOCAL_ESC').setParseAction(parseInfoFunc((PN_LOCAL_ESC)))


# [172]   HEX       ::=   [0-9] | [A-F] | [a-f] 
HEX_e = r'[0-9A-Fa-f]'
HEX_p = Regex(HEX_e)
class HEX(Terminal_): pass
if do_parseactions: HEX_p.setName('HEX').setParseAction(parseInfoFunc((HEX)))

# [171]   PERCENT   ::=   '%' HEX HEX
PERCENT_e = r'%({})({})'.format( HEX_e, HEX_e)
PERCENT_p = Regex(PERCENT_e)
class PERCENT(Terminal_): pass
if do_parseactions: PERCENT_p.setName('PERCENT').setParseAction(parseInfoFunc((PERCENT)))

# [170]   PLX       ::=   PERCENT | PN_LOCAL_ESC 
PLX_e = r'({})|({})'.format( PERCENT_e, PN_LOCAL_ESC_e)
PLX_p = Regex(PLX_e)
class PLX(Terminal_): pass
if do_parseactions: PLX_p.setName('PLX').setParseAction(parseInfoFunc((PLX)))

# [164]   PN_CHARS_BASE     ::=   [A-Z] | [a-z] | [#x00C0-#x00D6] | [#x00D8-#x00F6] | [#x00F8-#x02FF] | [#x0370-#x037D] | [#x037F-#x1FFF] | [#x200C-#x200D] | [#x2070-#x218F] | [#x2C00-#x2FEF] | [#x3001-#xD7FF] | [#xF900-#xFDCF] | [#xFDF0-#xFFFD] | [#x10000-#xEFFFF] 
PN_CHARS_BASE_e = r'[A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\U00010000-\U000EFFFF]'
PN_CHARS_BASE_p = Regex(PN_CHARS_BASE_e)
class PN_CHARS_BASE(Terminal_): pass
if do_parseactions: PN_CHARS_BASE_p.setName('PN_CHARS_BASE').setParseAction(parseInfoFunc((PN_CHARS_BASE)))

# [165]   PN_CHARS_U        ::=   PN_CHARS_BASE | '_' 
PN_CHARS_U_e = r'({})|({})'.format( PN_CHARS_BASE_e, r'_')
PN_CHARS_U_p = Regex(PN_CHARS_U_e)
class PN_CHARS_U(Terminal_): pass
if do_parseactions: PN_CHARS_U_p.setName('PN_CHARS_U').setParseAction(parseInfoFunc((PN_CHARS_U)))

# [167]   PN_CHARS          ::=   PN_CHARS_U | '-' | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] 
PN_CHARS_e = r'({})|({})|({})|({})|({})|({})'.format( PN_CHARS_U_e, r'\-', r'[0-9]',  r'\u00B7', r'[\u0300-\u036F]', r'[\u203F-\u2040]')
PN_CHARS_p = Regex(PN_CHARS_e) 
class PN_CHARS(Terminal_): pass
if do_parseactions: PN_CHARS_p.setName('PN_CHARS').setParseAction(parseInfoFunc((PN_CHARS)))

# [169]   PN_LOCAL          ::=   (PN_CHARS_U | ':' | [0-9] | PLX ) ((PN_CHARS | '.' | ':' | PLX)* (PN_CHARS | ':' | PLX) )?
PN_LOCAL_e = r'(({})|({})|({})|({}))((({})|({})|({})|({}))*(({})|({})|({})))?'.format( PN_CHARS_U_e, r':', r'[0-9]', PLX_e, PN_CHARS_e, r'\.', r':', PLX_e, PN_CHARS_e, r':', PLX_e) 
PN_LOCAL_p = Regex(PN_LOCAL_e)
class PN_LOCAL(Terminal_): pass
if do_parseactions: PN_LOCAL_p.setName('PN_LOCAL').setParseAction(parseInfoFunc((PN_LOCAL)))
            
# [168]   PN_PREFIX         ::=   PN_CHARS_BASE ((PN_CHARS|'.')* PN_CHARS)?
PN_PREFIX_e = r'({})((({})|({}))*({}))?'.format( PN_CHARS_BASE_e, PN_CHARS_e, r'\.', PN_CHARS_e)
PN_PREFIX_p = Regex(PN_PREFIX_e)
class PN_PREFIX(Terminal_): pass
if do_parseactions: PN_PREFIX_p.setName('PN_PREFIX').setParseAction(parseInfoFunc((PN_PREFIX)))

# [166]   VARNAME   ::=   ( PN_CHARS_U | [0-9] ) ( PN_CHARS_U | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] )* 
VARNAME_e = r'(({})|({}))(({})|({})|({})|({})|({}))*'.format( PN_CHARS_U_e, r'[0-9]', PN_CHARS_U_e, r'[0-9]', r'\u00B7', r'[\u0030-036F]', r'[\u0203-\u2040]')
VARNAME_p = Regex(VARNAME_e)
class VARNAME(Terminal_): pass
if do_parseactions: VARNAME_p.setName('VARNAME').setParseAction(parseInfoFunc((VARNAME)))

# [163]   ANON      ::=   '[' WS* ']' 
ANON_p = Group(Literal('[') + Literal(']'))
class ANON(Terminal_): pass
if do_parseactions: ANON_p.setName('ANON').setParseAction(parseInfoFunc((ANON)))

# [162]   WS        ::=   #x20 | #x9 | #xD | #xA 
# WS is not used
# In the SPARQL EBNF this production is used for defining NIL and ANON, but in this pyparsing implementation those are implemented differently

# [161]   NIL       ::=   '(' WS* ')' 
NIL_p = Group(Literal('(') + Literal(')'))
class NIL(Terminal_): pass
if do_parseactions: NIL_p.setName('NIL').setParseAction(parseInfoFunc((NIL)))

# [160]   ECHAR     ::=   '\' [tbnrf\"']
ECHAR_e = r'\\[tbnrf\\"\']'
ECHAR_p = Regex(ECHAR_e) 
class ECHAR(Terminal_): pass
if do_parseactions: ECHAR_p.setName('ECHAR').setParseAction(parseInfoFunc((ECHAR)))
 
# [159]   STRING_LITERAL_LONG2      ::=   '"""' ( ( '"' | '""' )? ( [^"\] | ECHAR ) )* '"""'  
STRING_LITERAL_LONG2_e = r'"""((""|")?(({})|({})))*"""'.format(r'[^"\\]', ECHAR_e)
STRING_LITERAL_LONG2_p = Regex(STRING_LITERAL_LONG2_e)
class STRING_LITERAL_LONG2(Terminal_):  
    pass
STRING_LITERAL_LONG2_p.parseWithTabs()
if do_parseactions: STRING_LITERAL_LONG2_p.setParseAction(parseInfoFunc(STRING_LITERAL_LONG2))

# [158]   STRING_LITERAL_LONG1      ::=   "'''" ( ( "'" | "''" )? ( [^'\] | ECHAR ) )* "'''" 
STRING_LITERAL_LONG1_e = r"'''(('|'')?(({})|({})))*'''".format(r"[^'\\]", ECHAR_e)
STRING_LITERAL_LONG1_p = Regex(STRING_LITERAL_LONG1_e)  
class STRING_LITERAL_LONG1(Terminal_):  
    pass
STRING_LITERAL_LONG1_p.parseWithTabs()
if do_parseactions: STRING_LITERAL_LONG1_p.setParseAction(parseInfoFunc(STRING_LITERAL_LONG1))

# [157]   STRING_LITERAL2   ::=   '"' ( ([^#x22#x5C#xA#xD]) | ECHAR )* '"' 
STRING_LITERAL2_e = r'"(({})|({}))*"'.format(ECHAR_e, r'[^\u0022\u005C\u000A\u000D]')
STRING_LITERAL2_p = Regex(STRING_LITERAL2_e)
class STRING_LITERAL2(Terminal_):  
    pass
STRING_LITERAL2_p.parseWithTabs()
if do_parseactions: STRING_LITERAL2_p.setParseAction(parseInfoFunc(STRING_LITERAL2))
                           
# [156]   STRING_LITERAL1   ::=   "'" ( ([^#x27#x5C#xA#xD]) | ECHAR )* "'" 
STRING_LITERAL1_e = r"'(({})|({}))*'".format(ECHAR_e, r'[^\u0027\u005C\u000A\u000D]')
STRING_LITERAL1_p = Regex(STRING_LITERAL1_e)
class STRING_LITERAL1(Terminal_):  
    pass
STRING_LITERAL1_p.parseWithTabs()
if do_parseactions: STRING_LITERAL1_p.setParseAction(parseInfoFunc(STRING_LITERAL1))
                            
# [155]   EXPONENT          ::=   [eE] [+-]? [0-9]+ 
EXPONENT_e = r'[eE][+-][0-9]+'
EXPONENT_p = Regex(EXPONENT_e)
class EXPONENT(Terminal_): pass
if do_parseactions: EXPONENT_p.setName('EXPONENT').setParseAction(parseInfoFunc((EXPONENT)))

# [148]   DOUBLE    ::=   [0-9]+ '.' [0-9]* EXPONENT | '.' ([0-9])+ EXPONENT | ([0-9])+ EXPONENT 
DOUBLE_e = r'([0-9]+\.[0-9]*({}))|(\.[0-9]+({}))|([0-9]+({}))'.format(EXPONENT_e, EXPONENT_e, EXPONENT_e)
DOUBLE_p = Regex(DOUBLE_e)
class DOUBLE(Terminal_): pass
if do_parseactions: DOUBLE_p.setName('DOUBLE').setParseAction(parseInfoFunc((DOUBLE)))

# [154]   DOUBLE_NEGATIVE   ::=   '-' DOUBLE 
DOUBLE_NEGATIVE_e = r'\-({})'.format(DOUBLE_e)
DOUBLE_NEGATIVE_p = Regex(DOUBLE_NEGATIVE_e)
class DOUBLE_NEGATIVE(Terminal_): pass
if do_parseactions: DOUBLE_NEGATIVE_p.setName('DOUBLE_NEGATIVE').setParseAction(parseInfoFunc((DOUBLE_NEGATIVE)))

# [151]   DOUBLE_POSITIVE   ::=   '+' DOUBLE 
DOUBLE_POSITIVE_e = r'\+({})'.format(DOUBLE_e)
DOUBLE_POSITIVE_p = Regex(DOUBLE_POSITIVE_e)
class DOUBLE_POSITIVE(Terminal_): pass
if do_parseactions: DOUBLE_POSITIVE_p.setName('DOUBLE_POSITIVE').setParseAction(parseInfoFunc((DOUBLE_POSITIVE)))

# [147]   DECIMAL   ::=   [0-9]* '.' [0-9]+ 
DECIMAL_e = r'[0-9]*\.[0-9]+'
DECIMAL_p = Regex(DECIMAL_e)
class DECIMAL(Terminal_): pass
if do_parseactions: DECIMAL_p.setName('DECIMAL').setParseAction(parseInfoFunc((DECIMAL)))

# [153]   DECIMAL_NEGATIVE          ::=   '-' DECIMAL 
DECIMAL_NEGATIVE_e = r'\-({})'.format(DECIMAL_e)
DECIMAL_NEGATIVE_p = Regex(DECIMAL_NEGATIVE_e)
class DECIMAL_NEGATIVE(Terminal_): pass
if do_parseactions: DECIMAL_NEGATIVE_p.setName('DECIMAL_NEGATIVE').setParseAction(parseInfoFunc((DECIMAL_NEGATIVE)))

# [150]   DECIMAL_POSITIVE          ::=   '+' DECIMAL 
DECIMAL_POSITIVE_e = r'\+({})'.format(DECIMAL_e)
DECIMAL_POSITIVE_p = Regex(DECIMAL_POSITIVE_e)
class DECIMAL_POSITIVE(Terminal_): pass
if do_parseactions: DECIMAL_POSITIVE_p.setName('DECIMAL_POSITIVE').setParseAction(parseInfoFunc((DECIMAL_POSITIVE)))

# [146]   INTEGER   ::=   [0-9]+ 
INTEGER_e = r'[0-9]+'
INTEGER_p = Regex(INTEGER_e)
class INTEGER(Terminal_): pass
if do_parseactions: INTEGER_p.setName('INTEGER').setParseAction(parseInfoFunc((INTEGER)))

# [152]   INTEGER_NEGATIVE          ::=   '-' INTEGER
INTEGER_NEGATIVE_e = r'\-({})'.format(INTEGER_e)
INTEGER_NEGATIVE_p = Regex(INTEGER_NEGATIVE_e)
class INTEGER_NEGATIVE(Terminal_): pass
if do_parseactions: INTEGER_NEGATIVE_p.setName('INTEGER_NEGATIVE').setParseAction(parseInfoFunc((INTEGER_NEGATIVE)))

# [149]   INTEGER_POSITIVE          ::=   '+' INTEGER 
INTEGER_POSITIVE_e = r'\+({})'.format(INTEGER_e)
INTEGER_POSITIVE_p = Regex(INTEGER_POSITIVE_e)
class INTEGER_POSITIVE(Terminal_): pass
if do_parseactions: INTEGER_POSITIVE_p.setName('INTEGER_POSITIVE').setParseAction(parseInfoFunc((INTEGER_POSITIVE)))

# [145]   LANGTAG   ::=   '@' [a-zA-Z]+ ('-' [a-zA-Z0-9]+)* 
LANGTAG_e = r'@[a-zA-Z]+(\-[a-zA-Z0-9]+)*'
LANGTAG_p = Regex(LANGTAG_e)
class LANGTAG(Terminal_): pass
if do_parseactions: LANGTAG_p.setName('LANGTAG').setParseAction(parseInfoFunc((LANGTAG)))

# [144]   VAR2      ::=   '$' VARNAME 
VAR2_e = r'\$({})'.format(VARNAME_e)
VAR2_p = Regex(VAR2_e)
class VAR2(Terminal_): pass
if do_parseactions: VAR2_p.setParseAction(parseInfoFunc(VAR2))

# [143]   VAR1      ::=   '?' VARNAME 
VAR1_e = r'\?({})'.format(VARNAME_e)
VAR1_p = Regex(VAR1_e)
class VAR1(Terminal_): pass
if do_parseactions: VAR1_p.setParseAction(parseInfoFunc(VAR1))

# [142]   BLANK_NODE_LABEL          ::=   '_:' ( PN_CHARS_U | [0-9] ) ((PN_CHARS|'.')* PN_CHARS)?
BLANK_NODE_LABEL_e = r'_:(({})|[0-9])((({})|\.)*({}))?'.format(PN_CHARS_U_e, PN_CHARS_e, PN_CHARS_e)
BLANK_NODE_LABEL_p = Regex(BLANK_NODE_LABEL_e)
class BLANK_NODE_LABEL(Terminal_): pass
if do_parseactions: BLANK_NODE_LABEL_p.setName('BLANK_NODE_LABEL').setParseAction(parseInfoFunc((BLANK_NODE_LABEL)))

# [140]   PNAME_NS          ::=   PN_PREFIX? ':'
PNAME_NS_e = r'({})?:'.format(PN_PREFIX_e)
PNAME_NS_p = Regex(PNAME_NS_e)
class PNAME_NS(Terminal_): pass
if do_parseactions: PNAME_NS_p.setName('PNAME_NS').setParseAction(parseInfoFunc((PNAME_NS)))

# [141]   PNAME_LN          ::=   PNAME_NS PN_LOCAL 
PNAME_LN_e = r'({})({})'.format(PNAME_NS_e, PN_LOCAL_e)
PNAME_LN_p = Regex(PNAME_LN_e)
class PNAME_LN(Terminal_): pass
if do_parseactions: PNAME_LN_p.setName('PNAME_LN').setParseAction(parseInfoFunc((PNAME_LN)))

# [139]   IRIREF    ::=   '<' ([^<>"{}|^`\]-[#x00-#x20])* '>' 
IRIREF_e = r'<[^<>"{}|^`\\\\\u0000-\u0020]*>'
IRIREF_p = Regex(IRIREF_e)
class IRIREF(Terminal_): pass
if do_parseactions: IRIREF_p.setName('IRIREF').setParseAction(parseInfoFunc((IRIREF)))

#
# Parsers and classes for non-terminals
#

# [138]   BlankNode         ::=   BLANK_NODE_LABEL | ANON 
BlankNode_p = Group(BLANK_NODE_LABEL_p | ANON_p)
class BlankNode(NonTerminal_): pass
if do_parseactions: BlankNode_p.setName('BlankNode').setParseAction(parseInfoFunc((BlankNode)))

# [137]   PrefixedName      ::=   PNAME_LN | PNAME_NS 
PrefixedName_p = Group(PNAME_LN_p ^ PNAME_NS_p)
class PrefixedName(NonTerminal_): pass
if do_parseactions: PrefixedName_p.setName('PrefixedName').setParseAction(parseInfoFunc((PrefixedName)))

# [136]   iri       ::=   IRIREF | PrefixedName 
iri_p = Group(Group(IRIREF_p ^ PrefixedName_p))
class iri(NonTerminal_): pass
if do_parseactions: iri_p.setName('iri').setParseAction(parseInfoFunc((iri)))

# [135]   String    ::=   STRING_LITERAL1 | STRING_LITERAL2 | STRING_LITERAL_LONG1 | STRING_LITERAL_LONG2 
String_p = Group(STRING_LITERAL1_p ^ STRING_LITERAL2_p ^ STRING_LITERAL_LONG1_p ^ STRING_LITERAL_LONG2_p)
class String(NonTerminal_):  
    pass
String_p.parseWithTabs()
if do_parseactions: String_p.setName('String').setParseAction(parseInfoFunc((String)))
 
# [134]   BooleanLiteral    ::=   'true' | 'false' 
BooleanLiteral_p = Group(Literal('true') | Literal('false'))
class BooleanLiteral(NonTerminal_): pass
if do_parseactions: BooleanLiteral_p.setName('BooleanLiteral').setParseAction(parseInfoFunc((BooleanLiteral)))
 
# # [133]   NumericLiteralNegative    ::=   INTEGER_NEGATIVE | DECIMAL_NEGATIVE | DOUBLE_NEGATIVE 
NumericLiteralNegative_p = Group(INTEGER_NEGATIVE_p ^ DECIMAL_NEGATIVE_p ^ DOUBLE_NEGATIVE_p)
class NumericLiteralNegative(NonTerminal_): pass
if do_parseactions: NumericLiteralNegative_p.setName('NumericLiteralNegative').setParseAction(parseInfoFunc((NumericLiteralNegative)))
 
# # [132]   NumericLiteralPositive    ::=   INTEGER_POSITIVE | DECIMAL_POSITIVE | DOUBLE_POSITIVE 
NumericLiteralPositive_p = Group(INTEGER_POSITIVE_p ^ DECIMAL_POSITIVE_p ^ DOUBLE_POSITIVE_p)
class NumericLiteralPositive(NonTerminal_): pass
if do_parseactions: NumericLiteralPositive_p.setName('NumericLiteralPositive').setParseAction(parseInfoFunc((NumericLiteralPositive)))
 
# # [131]   NumericLiteralUnsigned    ::=   INTEGER | DECIMAL | DOUBLE 
NumericLiteralUnsigned_p = Group(INTEGER_p ^ DECIMAL_p ^ DOUBLE_p)
class NumericLiteralUnsigned(NonTerminal_): pass
if do_parseactions: NumericLiteralUnsigned_p.setName('NumericLiteralUnsigned').setParseAction(parseInfoFunc((NumericLiteralUnsigned)))
# 
# # [130]   NumericLiteral    ::=   NumericLiteralUnsigned | NumericLiteralPositive | NumericLiteralNegative 
NumericLiteral_p = Group(NumericLiteralUnsigned_p | NumericLiteralPositive_p | NumericLiteralNegative_p)
class NumericLiteral(NonTerminal_): pass
if do_parseactions: NumericLiteral_p.setName('NumericLiteral').setParseAction(parseInfoFunc((NumericLiteral)))

# [129]   RDFLiteral        ::=   String ( LANGTAG | ( '^^' iri ) )? 
RDFLiteral_p = Group(String_p('lexical_form') + Optional(Group ((LANGTAG_p('langtag') ^ ('^^' + iri_p('datatype_uri'))))))
class RDFLiteral(NonTerminal_): pass
if do_parseactions: RDFLiteral_p.setName('RDFLiteral').setParseAction(parseInfoFunc((RDFLiteral)))

Expression_p = Forward()
class Expression(NonTerminal_): pass
if do_parseactions: Expression_p.setName('Expression').setParseAction(parseInfoFunc((Expression)))

# Auxiliary pattern
Expression_list_p = separatedList(Expression_p)
 
# [71]    ArgList   ::=   NIL | '(' 'DISTINCT'? Expression ( ',' Expression )* ')' 
ArgList_p = Group(NIL_p('nil')) | (LPAR_p + Optional(DISTINCT_kw_p('distinct')) + Expression_list_p('argument') + RPAR_p)
class ArgList(NonTerminal_): pass
if do_parseactions: ArgList_p.setName('ArgList').setParseAction(parseInfoFunc((ArgList)))


# [128]   iriOrFunction     ::=   iri ArgList? 
iriOrFunction_p = Group(iri_p('iri') + Optional(Group(ArgList_p))('ArgList'))
class iriOrFunction(NonTerminal_): pass
if do_parseactions: iriOrFunction_p.setName('iriOrFunction').setParseAction(parseInfoFunc((iriOrFunction)))

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
class Aggregate(NonTerminal_): pass
if do_parseactions: Aggregate_p.setName('Aggregate').setParseAction(parseInfoFunc((Aggregate)))

GroupGraphPattern_p = Forward()
class GroupGraphPattern(NonTerminal_): pass
if do_parseactions: GroupGraphPattern_p.setName('GroupGraphPattern').setParseAction(parseInfoFunc((GroupGraphPattern)))
 
# [126]   NotExistsFunc     ::=   'NOT' 'EXISTS' GroupGraphPattern 
NotExistsFunc_p = Group(NOT_EXISTS_kw_p + GroupGraphPattern_p('groupgraph'))
class NotExistsFunc(NonTerminal_): pass
if do_parseactions: NotExistsFunc_p.setName('NotExistsFunc').setParseAction(parseInfoFunc((NotExistsFunc)))
 
# [125]   ExistsFunc        ::=   'EXISTS' GroupGraphPattern 
ExistsFunc_p = Group(EXISTS_kw_p + GroupGraphPattern_p('groupgraph'))
class ExistsFunc(NonTerminal_): pass
if do_parseactions: ExistsFunc_p.setName('ExistsFunc').setParseAction(parseInfoFunc((ExistsFunc)))
 
# [124]   StrReplaceExpression      ::=   'REPLACE' '(' Expression ',' Expression ',' Expression ( ',' Expression )? ')' 
StrReplaceExpression_p = Group(REPLACE_kw_p + LPAR_p + Expression_p('arg') + COMMA_p + Expression_p('pattern') + COMMA_p + Expression_p('replacement') + Optional(COMMA_p + Expression_p('flags')) + RPAR_p)
class StrReplaceExpression(NonTerminal_): pass
if do_parseactions: StrReplaceExpression_p.setName('StrReplaceExpression').setParseAction(parseInfoFunc((StrReplaceExpression)))
 
# [123]   SubstringExpression       ::=   'SUBSTR' '(' Expression ',' Expression ( ',' Expression )? ')' 
SubstringExpression_p = Group(SUBSTR_kw_p + LPAR_p + Expression_p('source') + COMMA_p + Expression_p('startloc') + Optional(COMMA_p + Expression_p('length')) + RPAR_p)
class SubstringExpression(NonTerminal_): pass
if do_parseactions: SubstringExpression_p.setName('SubstringExpression').setParseAction(parseInfoFunc((SubstringExpression)))
 
# [122]   RegexExpression   ::=   'REGEX' '(' Expression ',' Expression ( ',' Expression )? ')' 
RegexExpression_p = Group(REGEX_kw_p + LPAR_p + Expression_p('text') + COMMA_p + Expression_p('pattern') + Optional(COMMA_p + Expression_p('flags')) + RPAR_p)
class RegexExpression(NonTerminal_): pass
if do_parseactions: RegexExpression_p.setName('RegexExpression').setParseAction(parseInfoFunc((RegexExpression)))

# [108]   Var       ::=   VAR1 | VAR2 
Var_p = Group(VAR1_p | VAR2_p)
class Var(NonTerminal_): pass
if do_parseactions: Var_p.setName('Var').setParseAction(parseInfoFunc((Var)))

ExpressionList_p = Forward()
class ExpressionList(NonTerminal_): pass
if do_parseactions: ExpressionList_p.setName('ExpressionList').setParseAction(parseInfoFunc((ExpressionList)))


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
class BuiltInCall(NonTerminal_): pass
if do_parseactions: BuiltInCall_p.setName('BuiltInCall').setParseAction(parseInfoFunc((BuiltInCall)))

# [120]   BrackettedExpression      ::=   '(' Expression ')' 
BracketedExpression_p = Group(LPAR_p + Expression_p('expression') + RPAR_p)
class BracketedExpression(NonTerminal_): pass
if do_parseactions: BracketedExpression_p.setName('BracketedExpression').setParseAction(parseInfoFunc((BracketedExpression)))

# [119]   PrimaryExpression         ::=   BrackettedExpression | BuiltInCall | iriOrFunction | RDFLiteral | NumericLiteral | BooleanLiteral | Var 
PrimaryExpression_p = Group(BracketedExpression_p | BuiltInCall_p | iriOrFunction_p('iriOrFunction') | RDFLiteral_p | NumericLiteral_p | BooleanLiteral_p | Var_p)
class PrimaryExpression(NonTerminal_): pass
if do_parseactions: PrimaryExpression_p.setName('PrimaryExpression').setParseAction(parseInfoFunc((PrimaryExpression)))

# [118]   UnaryExpression   ::=     '!' PrimaryExpression 
#             | '+' PrimaryExpression 
#             | '-' PrimaryExpression 
#             | PrimaryExpression 
UnaryExpression_p = Group(NOT_op_p + PrimaryExpression_p | PLUS_op_p + PrimaryExpression_p | MINUS_op_p + PrimaryExpression_p | PrimaryExpression_p)
class UnaryExpression(NonTerminal_): pass
if do_parseactions: UnaryExpression_p.setName('UnaryExpression').setParseAction(parseInfoFunc((UnaryExpression)))

# [117]   MultiplicativeExpression          ::=   UnaryExpression ( '*' UnaryExpression | '/' UnaryExpression )* 
MultiplicativeExpression_p = Group(UnaryExpression_p + ZeroOrMore( TIMES_op_p + UnaryExpression_p | DIV_op_p + UnaryExpression_p ))
class MultiplicativeExpression(NonTerminal_): pass
if do_parseactions: MultiplicativeExpression_p.setName('MultiplicativeExpression').setParseAction(parseInfoFunc((MultiplicativeExpression)))

# [116]   AdditiveExpression        ::=   MultiplicativeExpression ( '+' MultiplicativeExpression | '-' MultiplicativeExpression | ( NumericLiteralPositive | NumericLiteralNegative ) ( ( '*' UnaryExpression ) | ( '/' UnaryExpression ) )* )* 
AdditiveExpression_p = Group(MultiplicativeExpression_p + ZeroOrMore (PLUS_op_p + MultiplicativeExpression_p | MINUS_op_p  + MultiplicativeExpression_p | (NumericLiteralPositive_p | NumericLiteralNegative_p) + ZeroOrMore (TIMES_op_p + UnaryExpression_p | DIV_op_p + UnaryExpression_p)))
class AdditiveExpression(NonTerminal_): pass
if do_parseactions: AdditiveExpression_p.setName('AdditiveExpression').setParseAction(parseInfoFunc((AdditiveExpression)))

# [115]   NumericExpression         ::=   AdditiveExpression 
NumericExpression_p = Group(AdditiveExpression_p + Empty())
class NumericExpression(NonTerminal_): pass
if do_parseactions: NumericExpression_p.setName('NumericExpression').setParseAction(parseInfoFunc((NumericExpression)))

# [114]   RelationalExpression      ::=   NumericExpression ( '=' NumericExpression | '!=' NumericExpression | '<' NumericExpression | '>' NumericExpression | '<=' NumericExpression | '>=' NumericExpression | 'IN' ExpressionList | 'NOT' 'IN' ExpressionList )? 
RelationalExpression_p = Group(NumericExpression_p + Optional( EQ_op_p + NumericExpression_p | \
                                                         NE_op_p + NumericExpression_p | \
                                                         LT_op_p + NumericExpression_p | \
                                                         GT_op_p + NumericExpression_p | \
                                                         LE_op_p + NumericExpression_p | \
                                                         GE_op_p + NumericExpression_p | \
                                                         IN_kw_p + ExpressionList_p | \
                                                         NOT_IN_kw_p + ExpressionList_p) )
class RelationalExpression(NonTerminal_): pass
if do_parseactions: RelationalExpression_p.setName('RelationalExpression').setParseAction(parseInfoFunc((RelationalExpression)))

# [113]   ValueLogical      ::=   RelationalExpression 
ValueLogical_p = Group(RelationalExpression_p + Empty())
class ValueLogical(NonTerminal_): pass
if do_parseactions: ValueLogical_p.setName('ValueLogical').setParseAction(parseInfoFunc((ValueLogical)))

# [112]   ConditionalAndExpression          ::=   ValueLogical ( '&&' ValueLogical )* 
ConditionalAndExpression_p = Group(ValueLogical_p + ZeroOrMore(AND_op_p + ValueLogical_p))
class ConditionalAndExpression(NonTerminal_): pass
if do_parseactions: ConditionalAndExpression_p.setName('ConditionalAndExpression').setParseAction(parseInfoFunc((ConditionalAndExpression)))

# [111]   ConditionalOrExpression   ::=   ConditionalAndExpression ( '||' ConditionalAndExpression )* 
ConditionalOrExpression_p = Group(ConditionalAndExpression_p + ZeroOrMore(OR_op_p + ConditionalAndExpression_p))
class ConditionalOrExpression(NonTerminal_): pass
if do_parseactions: ConditionalOrExpression_p.setName('ConditionalOrExpression').setParseAction(parseInfoFunc((ConditionalOrExpression)))

# [110]   Expression        ::=   ConditionalOrExpression 
Expression_p << Group(ConditionalOrExpression_p + Empty())

# [109]   GraphTerm         ::=   iri | RDFLiteral | NumericLiteral | BooleanLiteral | BlankNode | NIL 
GraphTerm_p =   Group(iri_p | \
                RDFLiteral_p | \
                NumericLiteral_p | \
                BooleanLiteral_p | \
                BlankNode_p | \
                NIL_p )
class GraphTerm(NonTerminal_): pass
if do_parseactions: GraphTerm_p.setName('GraphTerm').setParseAction(parseInfoFunc((GraphTerm)))
                
# [107]   VarOrIri          ::=   Var | iri 
VarOrIri_p = Group(Var_p | iri_p)
class VarOrIri(NonTerminal_): pass
if do_parseactions: VarOrIri_p.setName('VarOrIri').setParseAction(parseInfoFunc((VarOrIri)))

# [106]   VarOrTerm         ::=   Var | GraphTerm 
VarOrTerm_p = Group(Var_p | GraphTerm_p)
class VarOrTerm(NonTerminal_): pass
if do_parseactions: VarOrTerm_p.setName('VarOrTerm').setParseAction(parseInfoFunc((VarOrTerm)))

TriplesNodePath_p = Forward()
class TriplesNodePath(NonTerminal_): pass
if do_parseactions: TriplesNodePath_p.setName('TriplesNodePath').setParseAction(parseInfoFunc((TriplesNodePath)))

# [105]   GraphNodePath     ::=   VarOrTerm | TriplesNodePath 
GraphNodePath_p = Group(VarOrTerm_p ^ TriplesNodePath_p )

TriplesNode_p = Forward()
class TriplesNode(NonTerminal_): pass
if do_parseactions: TriplesNode_p.setName('TriplesNode').setParseAction(parseInfoFunc((TriplesNode)))

# [104]   GraphNode         ::=   VarOrTerm | TriplesNode 
GraphNode_p = Group(VarOrTerm_p ^ TriplesNode_p)
class GraphNode(NonTerminal_): pass
if do_parseactions: GraphNode_p.setName('GraphNode').setParseAction(parseInfoFunc((GraphNode)))

# [103]   CollectionPath    ::=   '(' GraphNodePath+ ')' 
CollectionPath_p = Group( LPAR_p + OneOrMore(GraphNodePath_p) + RPAR_p)
class CollectionPath(NonTerminal_): pass
if do_parseactions: CollectionPath_p.setName('CollectionPath').setParseAction(parseInfoFunc((CollectionPath)))

# [102]   Collection        ::=   '(' GraphNode+ ')' 
Collection_p = Group( LPAR_p + OneOrMore(GraphNode_p) + RPAR_p)
class Collection(NonTerminal_): pass
if do_parseactions: Collection_p.setName('Collection').setParseAction(parseInfoFunc((Collection)))

PropertyListPathNotEmpty_p = Forward()
class PropertyListPathNotEmpty(NonTerminal_): pass
if do_parseactions: PropertyListPathNotEmpty_p.setName('PropertyListPathNotEmpty').setParseAction(parseInfoFunc((PropertyListPathNotEmpty)))

# [101]   BlankNodePropertyListPath         ::=   '[' PropertyListPathNotEmpty ']'
BlankNodePropertyListPath_p = Group(  LBRACK_p + PropertyListPathNotEmpty_p + RBRACK_p )
class BlankNodePropertyListPath(NonTerminal_): pass
if do_parseactions: BlankNodePropertyListPath_p.setName('BlankNodePropertyListPath').setParseAction(parseInfoFunc((BlankNodePropertyListPath)))

# [100]   TriplesNodePath   ::=   CollectionPath | BlankNodePropertyListPath 
TriplesNodePath_p << Group(CollectionPath_p | BlankNodePropertyListPath_p) 

PropertyListNotEmpty_p = Forward()
class PropertyListNotEmpty(NonTerminal_): pass
if do_parseactions: PropertyListNotEmpty_p.setName('PropertyListNotEmpty').setParseAction(parseInfoFunc((PropertyListNotEmpty)))

# [99]    BlankNodePropertyList     ::=   '[' PropertyListNotEmpty ']' 
BlankNodePropertyList_p = Group(  LBRACK_p + PropertyListNotEmpty_p + RBRACK_p )
class BlankNodePropertyList(NonTerminal_): pass
if do_parseactions: BlankNodePropertyList_p.setName('BlankNodePropertyList').setParseAction(parseInfoFunc((BlankNodePropertyList)))

# [98]    TriplesNode       ::=   Collection | BlankNodePropertyList 
TriplesNode_p << Group(Collection_p | BlankNodePropertyList_p)

# [97]    Integer   ::=   INTEGER 
Integer_p = Group(INTEGER_p + Empty())
class Integer(NonTerminal_): pass
if do_parseactions: Integer_p.setName('Integer').setParseAction(parseInfoFunc((Integer)))

# [96]    PathOneInPropertySet      ::=   iri | 'a' | '^' ( iri | 'a' ) 
PathOneInPropertySet_p = Group(  iri_p | TYPE_kw_p | (INVERSE_op_p  + ( iri_p | TYPE_kw_p )))
class PathOneInPropertySet(NonTerminal_): pass
if do_parseactions: PathOneInPropertySet_p.setName('PathOneInPropertySet').setParseAction(parseInfoFunc((PathOneInPropertySet)))

# Auxiliary pattern
PathOneInPropertySet_list_p = separatedList(PathOneInPropertySet_p, sep='|')

# [95]    PathNegatedPropertySet    ::=   PathOneInPropertySet | '(' ( PathOneInPropertySet ( '|' PathOneInPropertySet )* )? ')' 
PathNegatedPropertySet_p = Group(PathOneInPropertySet_p | (LPAR_p + Optional(PathOneInPropertySet_list_p('pathinone')) + RPAR_p))
class PathNegatedPropertySet(NonTerminal_): pass
if do_parseactions: PathNegatedPropertySet_p.setName('PathNegatedPropertySet').setParseAction(parseInfoFunc((PathNegatedPropertySet)))

Path_p = Forward()
class Path(NonTerminal_): pass
if do_parseactions: Path_p.setName('Path').setParseAction(parseInfoFunc((Path)))

# [94]    PathPrimary       ::=   iri | 'a' | '!' PathNegatedPropertySet | '(' Path ')' 
PathPrimary_p = Group(iri_p | TYPE_kw_p | (NOT_op_p + PathNegatedPropertySet_p) | (LPAR_p + Path_p + RPAR_p))
class PathPrimary(NonTerminal_): pass
if do_parseactions: PathPrimary_p.setName('PathPrimary').setParseAction(parseInfoFunc((PathPrimary)))

# [93]    PathMod   ::=   '?' | '*' | '+' 
PathMod_p = Group((~VAR1_p + Literal('?')) | Literal('*') | Literal('+'))
class PathMod(NonTerminal_): pass
if do_parseactions: PathMod_p.setName('PathMod').setParseAction(parseInfoFunc((PathMod)))

# [91]    PathElt   ::=   PathPrimary PathMod? 
PathElt_p = Group(PathPrimary_p + Optional(PathMod_p) )
class PathElt(NonTerminal_): pass
if do_parseactions: PathElt_p.setName('PathElt').setParseAction(parseInfoFunc((PathElt)))

# [92]    PathEltOrInverse          ::=   PathElt | '^' PathElt 
PathEltOrInverse_p = Group(PathElt_p | (INVERSE_op_p + PathElt_p))
class PathEltOrInverse(NonTerminal_): pass
if do_parseactions: PathEltOrInverse_p.setName('PathEltOrInverse').setParseAction(parseInfoFunc((PathEltOrInverse)))

# [90]    PathSequence      ::=   PathEltOrInverse ( '/' PathEltOrInverse )* 
PathSequence_p = Group(separatedList(PathEltOrInverse_p, sep='/'))
class PathSequence(NonTerminal_):pass
if do_parseactions: PathSequence_p.setName('PathSequence').setParseAction(parseInfoFunc((PathSequence)))

# [89]    PathAlternative   ::=   PathSequence ( '|' PathSequence )* 
PathAlternative_p = Group(separatedList(PathSequence_p, sep='|'))
class PathAlternative(NonTerminal_): pass
if do_parseactions: PathAlternative_p.setName('PathAlternative').setParseAction(parseInfoFunc((PathAlternative)))
 
# [88]    Path      ::=   PathAlternative
Path_p << Group(PathAlternative_p + Empty()) 

# [87]    ObjectPath        ::=   GraphNodePath 
ObjectPath_p = Group(GraphNodePath_p + Empty() )
class ObjectPath(NonTerminal_): pass
if do_parseactions: ObjectPath_p.setName('ObjectPath').setParseAction(parseInfoFunc((ObjectPath)))

# [86]    ObjectListPath    ::=   ObjectPath ( ',' ObjectPath )* 
ObjectListPath_p = Group(separatedList(ObjectPath_p))
class ObjectListPath(NonTerminal_): pass
if do_parseactions: ObjectListPath_p.setName('ObjectListPath').setParseAction(parseInfoFunc((ObjectListPath)))

# [85]    VerbSimple        ::=   Var 
VerbSimple_p = Group(Var_p + Empty() )
class VerbSimple(NonTerminal_): pass
if do_parseactions: VerbSimple_p.setName('VerbSimple').setParseAction(parseInfoFunc((VerbSimple)))

# [84]    VerbPath          ::=   Path
VerbPath_p = Group(Path_p + Empty() )
class VerbPath(NonTerminal_): pass
if do_parseactions: VerbPath_p.setName('VerbPath').setParseAction(parseInfoFunc((VerbPath)))

# [80]    Object    ::=   GraphNode 
Object_p = Group(GraphNode_p + Empty() )
class Object(NonTerminal_): pass
if do_parseactions: Object_p.setName('Object').setParseAction(parseInfoFunc((Object)))
 
# [79]    ObjectList        ::=   Object ( ',' Object )* 
ObjectList_p = Group(separatedList(Object_p))
class ObjectList(NonTerminal_): pass
if do_parseactions: ObjectList_p.setName('ObjectList').setParseAction(parseInfoFunc((ObjectList)))

# [83]    PropertyListPathNotEmpty          ::=   ( VerbPath | VerbSimple ) ObjectListPath ( ';' ( ( VerbPath | VerbSimple ) ObjectList )? )* 
PropertyListPathNotEmpty_p << Group((VerbPath_p | VerbSimple_p) + ObjectListPath_p +  ZeroOrMore(SEMICOL_p + Optional(( VerbPath_p | VerbSimple_p) + ObjectList_p)))

# [82]    PropertyListPath          ::=   PropertyListPathNotEmpty? 
PropertyListPath_p = Group(Optional(PropertyListPathNotEmpty_p))
class PropertyListPath(NonTerminal_): pass
if do_parseactions: PropertyListPath_p.setName('PropertyListPath').setParseAction(parseInfoFunc((PropertyListPath)))

# [81]    TriplesSameSubjectPath    ::=   VarOrTerm PropertyListPathNotEmpty | TriplesNodePath PropertyListPath 
TriplesSameSubjectPath_p = Group((VarOrTerm_p + PropertyListPathNotEmpty_p) | (TriplesNodePath_p + PropertyListPath_p))
class TriplesSameSubjectPath(NonTerminal_): pass
if do_parseactions: TriplesSameSubjectPath_p.setName('TriplesSameSubjectPath').setParseAction(parseInfoFunc((TriplesSameSubjectPath)))

# [78]    Verb      ::=   VarOrIri | 'a' 
Verb_p = Group(VarOrIri_p | TYPE_kw_p)
class Verb(NonTerminal_): pass
if do_parseactions: Verb_p.setName('Verb').setParseAction(parseInfoFunc((Verb)))

# [77]    PropertyListNotEmpty      ::=   Verb ObjectList ( ';' ( Verb ObjectList )? )* 
PropertyListNotEmpty_p << Group(Verb_p + ObjectList_p + ZeroOrMore(SEMICOL_p + Optional(Verb_p + ObjectList_p))) 

# [76]    PropertyList      ::=   PropertyListNotEmpty?
PropertyList_p = Group(Optional(PropertyListNotEmpty_p) )
class PropertyList(NonTerminal_): pass
if do_parseactions: PropertyList_p.setName('PropertyList').setParseAction(parseInfoFunc((PropertyList)))

# [75]    TriplesSameSubject        ::=   VarOrTerm PropertyListNotEmpty | TriplesNode PropertyList
TriplesSameSubject_p = Group((VarOrTerm_p + PropertyListNotEmpty_p) | (TriplesNode_p + PropertyList_p) )
class TriplesSameSubject(NonTerminal_): pass
if do_parseactions: TriplesSameSubject_p.setName('TriplesSameSubject').setParseAction(parseInfoFunc((TriplesSameSubject)))

# Auxiliary pattern
TriplesSameSubject_list_p = separatedList(TriplesSameSubject_p, sep='.')

# [74]    ConstructTriples          ::=   TriplesSameSubject ( '.' ConstructTriples? )? 
ConstructTriples_p = Group(TriplesSameSubject_list_p + Optional(PERIOD_p))
class ConstructTriples(NonTerminal_): pass
if do_parseactions: ConstructTriples_p.setName('ConstructTriples').setParseAction(parseInfoFunc((ConstructTriples)))

# [73]    ConstructTemplate         ::=   '{' ConstructTriples? '}'
ConstructTemplate_p = Group(  LCURL_p + Optional(ConstructTriples_p) + RCURL_p )
class ConstructTemplate(NonTerminal_): pass
if do_parseactions: ConstructTemplate_p.setName('ConstructTemplate').setParseAction(parseInfoFunc((ConstructTemplate)))

# [72]    ExpressionList    ::=   NIL | '(' Expression ( ',' Expression )* ')' 
ExpressionList_p << Group(NIL_p | (LPAR_p + Expression_list_p + RPAR_p))

# [70]    FunctionCall      ::=   iri ArgList 
FunctionCall_p = Group(iri_p + ArgList_p)
class FunctionCall(NonTerminal_): pass
if do_parseactions: FunctionCall_p.setName('FunctionCall').setParseAction(parseInfoFunc((FunctionCall)))

# [69]    Constraint        ::=   BrackettedExpression | BuiltInCall | FunctionCall 
Constraint_p = Group(BracketedExpression_p | BuiltInCall_p | FunctionCall_p)
class Constraint(NonTerminal_): pass
if do_parseactions: Constraint_p.setName('Constraint').setParseAction(parseInfoFunc((Constraint)))

# [68]    Filter    ::=   'FILTER' Constraint
Filter_p = Group(FILTER_kw_p + Constraint_p )
class Filter(NonTerminal_): pass
if do_parseactions: Filter_p.setName('Filter').setParseAction(parseInfoFunc((Filter)))

# [67]    GroupOrUnionGraphPattern          ::=   GroupGraphPattern ( 'UNION' GroupGraphPattern )* 
GroupOrUnionGraphPattern_p = Group(GroupGraphPattern_p + ZeroOrMore(UNION_kw_p + GroupGraphPattern_p) )
class GroupOrUnionGraphPattern(NonTerminal_): pass
if do_parseactions: GroupOrUnionGraphPattern_p.setName('GroupOrUnionGraphPattern').setParseAction(parseInfoFunc((GroupOrUnionGraphPattern)))

# [66]    MinusGraphPattern         ::=   'MINUS' GroupGraphPattern
MinusGraphPattern_p = Group(  MINUS_kw_p + GroupGraphPattern_p )
class MinusGraphPattern(NonTerminal_): pass
if do_parseactions: MinusGraphPattern_p.setName('MinusGraphPattern').setParseAction(parseInfoFunc((MinusGraphPattern)))

# [65]    DataBlockValue    ::=   iri | RDFLiteral | NumericLiteral | BooleanLiteral | 'UNDEF' 
DataBlockValue_p = Group(iri_p | RDFLiteral_p | NumericLiteral_p | BooleanLiteral_p | UNDEF_kw_p)
class DataBlockValue(NonTerminal_): pass
if do_parseactions: DataBlockValue_p.setName('DataBlockValue').setParseAction(parseInfoFunc((DataBlockValue)))

# [64]    InlineDataFull    ::=   ( NIL | '(' Var* ')' ) '{' ( '(' DataBlockValue* ')' | NIL )* '}' 
InlineDataFull_p = Group(( NIL_p | (LPAR_p + ZeroOrMore(Var_p) + RPAR_p)) + LCURL_p +  ZeroOrMore((LPAR_p + ZeroOrMore(DataBlockValue_p) + RPAR_p) | NIL_p) + RCURL_p )
class InlineDataFull(NonTerminal_): pass
if do_parseactions: InlineDataFull_p.setName('InlineDataFull').setParseAction(parseInfoFunc((InlineDataFull)))

# [63]    InlineDataOneVar          ::=   Var '{' DataBlockValue* '}' 
InlineDataOneVar_p = Group(Var_p + LCURL_p + ZeroOrMore(DataBlockValue_p) + RCURL_p )
class InlineDataOneVar(NonTerminal_): pass
if do_parseactions: InlineDataOneVar_p.setName('InlineDataOneVar').setParseAction(parseInfoFunc((InlineDataOneVar)))

# [62]    DataBlock         ::=   InlineDataOneVar | InlineDataFull 
DataBlock_p = Group(InlineDataOneVar_p | InlineDataFull_p)
class DataBlock(NonTerminal_): pass
if do_parseactions: DataBlock_p.setName('DataBlock').setParseAction(parseInfoFunc((DataBlock)))

# [61]    InlineData        ::=   'VALUES' DataBlock 
InlineData_p = Group(VALUES_kw_p + DataBlock_p )
class InlineData(NonTerminal_): pass
if do_parseactions: InlineData_p.setName('InlineData').setParseAction(parseInfoFunc((InlineData)))

# [60]    Bind      ::=   'BIND' '(' Expression 'AS' Var ')' 
Bind_p = Group(  BIND_kw_p + LPAR_p + Expression_p + AS_kw_p + Var_p + RPAR_p )
class Bind(NonTerminal_): pass
if do_parseactions: Bind_p.setName('Bind').setParseAction(parseInfoFunc((Bind)))

# [59]    ServiceGraphPattern       ::=   'SERVICE' 'SILENT'? VarOrIri GroupGraphPattern 
ServiceGraphPattern_p = Group(  SERVICE_kw_p + Optional(SILENT_kw_p) + VarOrIri_p + GroupGraphPattern_p )
class ServiceGraphPattern(NonTerminal_): pass
if do_parseactions: ServiceGraphPattern_p.setName('ServiceGraphPattern').setParseAction(parseInfoFunc((ServiceGraphPattern)))

# [58]    GraphGraphPattern         ::=   'GRAPH' VarOrIri GroupGraphPattern 
GraphGraphPattern_p = Group(  GRAPH_kw_p + VarOrIri_p + GroupGraphPattern_p )
class GraphGraphPattern(NonTerminal_): pass
if do_parseactions: GraphGraphPattern_p.setName('GraphGraphPattern').setParseAction(parseInfoFunc((GraphGraphPattern)))

# [57]    OptionalGraphPattern      ::=   'OPTIONAL' GroupGraphPattern 
OptionalGraphPattern_p = Group(  OPTIONAL_kw_p + GroupGraphPattern_p )
class OptionalGraphPattern(NonTerminal_): pass
if do_parseactions: OptionalGraphPattern_p.setName('OptionalGraphPattern').setParseAction(parseInfoFunc((OptionalGraphPattern)))

# [56]    GraphPatternNotTriples    ::=   GroupOrUnionGraphPattern | OptionalGraphPattern | MinusGraphPattern | GraphGraphPattern | ServiceGraphPattern | Filter | Bind | InlineData 
GraphPatternNotTriples_p = Group(GroupOrUnionGraphPattern_p | OptionalGraphPattern_p | MinusGraphPattern_p | GraphGraphPattern_p | ServiceGraphPattern_p | Filter_p | Bind_p | InlineData_p )
class GraphPatternNotTriples(NonTerminal_): pass
if do_parseactions: GraphPatternNotTriples_p.setName('GraphPatternNotTriples').setParseAction(parseInfoFunc((GraphPatternNotTriples)))

# Auxiliary pattern
TriplesSameSubjectPath_list_p = separatedList(TriplesSameSubjectPath_p, sep='.')
                                           
# [55]    TriplesBlock      ::=   TriplesSameSubjectPath ( '.' TriplesBlock? )? 
TriplesBlock_p = Group(TriplesSameSubjectPath_list_p('subjpath') + Optional(PERIOD_p))
class TriplesBlock(NonTerminal_): pass
if do_parseactions: TriplesBlock_p.setName('TriplesBlock').setParseAction(parseInfoFunc((TriplesBlock)))

# [54]    GroupGraphPatternSub      ::=   TriplesBlock? ( GraphPatternNotTriples '.'? TriplesBlock? )* 
GroupGraphPatternSub_p = Group(Optional(TriplesBlock_p) + ZeroOrMore(GraphPatternNotTriples_p + Optional(PERIOD_p) + Optional(TriplesBlock_p)) )
class GroupGraphPatternSub(NonTerminal_): pass
if do_parseactions: GroupGraphPatternSub_p.setName('GroupGraphPatternSub').setParseAction(parseInfoFunc((GroupGraphPatternSub)))

SubSelect_p = Forward()
class SubSelect(NonTerminal_): pass
if do_parseactions: SubSelect_p.setName('SubSelect').setParseAction(parseInfoFunc((SubSelect)))

# [53]    GroupGraphPattern         ::=   '{' ( SubSelect | GroupGraphPatternSub ) '}' 
GroupGraphPattern_p << Group(LCURL_p + (SubSelect_p | GroupGraphPatternSub_p)('pattern') + RCURL_p) 

# [52]    TriplesTemplate   ::=   TriplesSameSubject ( '.' TriplesTemplate? )? 
TriplesTemplate_p = Group(TriplesSameSubject_list_p + Optional(PERIOD_p)) 
class TriplesTemplate(NonTerminal_): pass
if do_parseactions: TriplesTemplate_p.setName('TriplesTemplate').setParseAction(parseInfoFunc((TriplesTemplate)))

# [51]    QuadsNotTriples   ::=   'GRAPH' VarOrIri '{' TriplesTemplate? '}' 
QuadsNotTriples_p = Group(GRAPH_kw_p + VarOrIri_p + LCURL_p + Optional(TriplesTemplate_p) + RCURL_p )
class QuadsNotTriples(NonTerminal_): pass
if do_parseactions: QuadsNotTriples_p.setName('QuadsNotTriples').setParseAction(parseInfoFunc((QuadsNotTriples)))

# [50]    Quads     ::=   TriplesTemplate? ( QuadsNotTriples '.'? TriplesTemplate? )* 
Quads_p = Group(Optional(TriplesTemplate_p) + ZeroOrMore(QuadsNotTriples_p + Optional(PERIOD_p) + Optional(TriplesTemplate_p)) )
class Quads(NonTerminal_): pass
if do_parseactions: Quads_p.setName('Quads').setParseAction(parseInfoFunc((Quads)))

# [49]    QuadData          ::=   '{' Quads '}' 
QuadData_p = Group(LCURL_p + Quads_p + RCURL_p )
class QuadData(NonTerminal_): pass
if do_parseactions: QuadData_p.setName('QuadData').setParseAction(parseInfoFunc((QuadData)))

# [48]    QuadPattern       ::=   '{' Quads '}' 
QuadPattern_p = Group(LCURL_p + Quads_p + RCURL_p )
class QuadPattern(NonTerminal_): pass
if do_parseactions: QuadPattern_p.setName('QuadPattern').setParseAction(parseInfoFunc((QuadPattern)))

# [46]    GraphRef          ::=   'GRAPH' iri 
GraphRef_p = Group(GRAPH_kw_p + iri_p )
class GraphRef(NonTerminal_): pass
if do_parseactions: GraphRef_p.setName('GraphRef').setParseAction(parseInfoFunc((GraphRef)))

# [47]    GraphRefAll       ::=   GraphRef | 'DEFAULT' | 'NAMED' | 'ALL' 
GraphRefAll_p = Group(GraphRef_p | DEFAULT_kw_p | NAMED_kw_p | ALL_kw_p )
class GraphRefAll(NonTerminal_): pass
if do_parseactions: GraphRefAll_p.setName('GraphRefAll').setParseAction(parseInfoFunc((GraphRefAll)))

# [45]    GraphOrDefault    ::=   'DEFAULT' | 'GRAPH'? iri 
GraphOrDefault_p = Group(  DEFAULT_kw_p | (Optional(GRAPH_kw_p) + iri_p) )
class GraphOrDefault(NonTerminal_): pass
if do_parseactions: GraphOrDefault_p.setName('GraphOrDefault').setParseAction(parseInfoFunc((GraphOrDefault)))

# [44]    UsingClause       ::=   'USING' ( iri | 'NAMED' iri ) 
UsingClause_p = Group(  USING_kw_p + (iri_p | (NAMED_kw_p + iri_p)) )
class UsingClause(NonTerminal_): pass
if do_parseactions: UsingClause_p.setName('UsingClause').setParseAction(parseInfoFunc((UsingClause)))

# [43]    InsertClause      ::=   'INSERT' QuadPattern 
InsertClause_p = Group(  INSERT_kw_p + QuadPattern_p )
class InsertClause(NonTerminal_): pass
if do_parseactions: InsertClause_p.setName('InsertClause').setParseAction(parseInfoFunc((InsertClause)))

# [42]    DeleteClause      ::=   'DELETE' QuadPattern 
DeleteClause_p = Group(  DELETE_kw_p + QuadPattern_p )
class DeleteClause(NonTerminal_): pass
if do_parseactions: DeleteClause_p.setName('DeleteClause').setParseAction(parseInfoFunc((DeleteClause)))

# [41]    Modify    ::=   ( 'WITH' iri )? ( DeleteClause InsertClause? | InsertClause ) UsingClause* 'WHERE' GroupGraphPattern 
Modify_p = Group(  Optional(WITH_kw_p + iri_p) + ( (DeleteClause_p + Optional(InsertClause_p) ) | InsertClause_p ) + ZeroOrMore(UsingClause_p) + WHERE_kw_p + GroupGraphPattern_p )
class Modify(NonTerminal_): pass
if do_parseactions: Modify_p.setName('Modify').setParseAction(parseInfoFunc((Modify)))

# [40]    DeleteWhere       ::=   'DELETE WHERE' QuadPattern 
DeleteWhere_p = Group(  DELETE_WHERE_kw_p + QuadPattern_p )
class DeleteWhere(NonTerminal_): pass
if do_parseactions: DeleteWhere_p.setName('DeleteWhere').setParseAction(parseInfoFunc((DeleteWhere)))

# [39]    DeleteData        ::=   'DELETE DATA' QuadData 
DeleteData_p = Group(DELETE_DATA_kw_p + QuadData_p )
class DeleteData(NonTerminal_): pass
if do_parseactions: DeleteData_p.setName('DeleteData').setParseAction(parseInfoFunc((DeleteData)))

# [38]    InsertData        ::=   'INSERT DATA' QuadData 
InsertData_p = Group(INSERT_DATA_kw_p + QuadData_p )
class InsertData(NonTerminal_): pass
if do_parseactions: InsertData_p.setName('InsertData').setParseAction(parseInfoFunc((InsertData)))

# [37]    Copy      ::=   'COPY' 'SILENT'? GraphOrDefault 'TO' GraphOrDefault 
Copy_p = Group(COPY_kw_p + Optional(SILENT_kw_p) + GraphOrDefault_p + TO_kw_p + GraphOrDefault_p )
class Copy(NonTerminal_): pass
if do_parseactions: Copy_p.setName('Copy').setParseAction(parseInfoFunc((Copy)))

# [36]    Move      ::=   'MOVE' 'SILENT'? GraphOrDefault 'TO' GraphOrDefault 
Move_p = Group(MOVE_kw_p + Optional(SILENT_kw_p) + GraphOrDefault_p + TO_kw_p + GraphOrDefault_p )
class Move(NonTerminal_): pass
if do_parseactions: Move_p.setName('Move').setParseAction(parseInfoFunc((Move)))

# [35]    Add       ::=   'ADD' 'SILENT'? GraphOrDefault 'TO' GraphOrDefault 
Add_p = Group(ADD_kw_p + Optional(SILENT_kw_p) + GraphOrDefault_p + TO_kw_p + GraphOrDefault_p )
class Add(NonTerminal_): pass
if do_parseactions: Add_p.setName('Add').setParseAction(parseInfoFunc((Add)))

# [34]    Create    ::=   'CREATE' 'SILENT'? GraphRef 
Create_p = Group(CREATE_kw_p + Optional(SILENT_kw_p) + GraphRef_p)
class Create(NonTerminal_): pass
if do_parseactions: Create_p.setName('Create').setParseAction(parseInfoFunc((Create)))

# [33]    Drop      ::=   'DROP' 'SILENT'? GraphRefAll 
Drop_p = Group(DROP_kw_p + Optional(SILENT_kw_p) + GraphRefAll_p)
class Drop(NonTerminal_): pass
if do_parseactions: Drop_p.setName('Drop').setParseAction(parseInfoFunc((Drop)))

# [32]    Clear     ::=   'CLEAR' 'SILENT'? GraphRefAll 
Clear_p = Group(CLEAR_kw_p + Optional(SILENT_kw_p) + GraphRefAll_p )
class Clear(NonTerminal_): pass
if do_parseactions: Clear_p.setName('Clear').setParseAction(parseInfoFunc((Clear)))

# [31]    Load      ::=   'LOAD' 'SILENT'? iri ( 'INTO' GraphRef )? 
Load_p = Group(LOAD_kw_p + Optional(SILENT_kw_p) + iri_p  + Optional(INTO_kw_p + GraphRef_p))
class Load(NonTerminal_): pass
if do_parseactions: Load_p.setName('Load').setParseAction(parseInfoFunc((Load)))

# [30]    Update1   ::=   Load | Clear | Drop | Add | Move | Copy | Create | InsertData | DeleteData | DeleteWhere | Modify 
Update1_p = Group(Load_p | Clear_p | Drop_p | Add_p | Move_p | Copy_p | Create_p | InsertData_p | DeleteData_p | DeleteWhere_p | Modify_p )
class Update1(NonTerminal_): pass
if do_parseactions: Update1_p.setParseAction(parseInfoFunc(Update1))

Prologue_p = Forward()
class Prologue(NonTerminal_): pass
if do_parseactions: Prologue_p.setName('Prologue').setParseAction(parseInfoFunc((Prologue)))

Update_p = Forward()
class Update(NonTerminal_): pass
if do_parseactions: Update_p.setName('Update').setParseAction(parseInfoFunc((Update)))

# [29]    Update    ::=   Prologue ( Update1 ( ';' Update )? )? 
Update_p << Group(Prologue_p + Optional(Update1_p + Optional(SEMICOL_p + Update_p))) 

# [28]    ValuesClause      ::=   ( 'VALUES' DataBlock )? 
ValuesClause_p = Group(Optional(VALUES_kw_p + DataBlock_p) )
class ValuesClause(NonTerminal_): pass
if do_parseactions: ValuesClause_p.setName('ValuesClause').setParseAction(parseInfoFunc((ValuesClause)))

# [27]    OffsetClause      ::=   'OFFSET' INTEGER 
OffsetClause_p = Group(  OFFSET_kw_p + INTEGER_p )
class OffsetClause(NonTerminal_): pass
if do_parseactions: OffsetClause_p.setName('OffsetClause').setParseAction(parseInfoFunc((OffsetClause)))

# [26]    LimitClause       ::=   'LIMIT' INTEGER 
LimitClause_p = Group(  LIMIT_kw_p + INTEGER_p )
class LimitClause(NonTerminal_): pass
if do_parseactions: LimitClause_p.setName('LimitClause').setParseAction(parseInfoFunc((LimitClause)))

# [25]    LimitOffsetClauses        ::=   LimitClause OffsetClause? | OffsetClause LimitClause? 
LimitOffsetClauses_p = Group(LimitClause_p + Optional(OffsetClause_p)) | (OffsetClause_p + Optional(LimitClause_p))
class LimitOffsetClauses(NonTerminal_): pass
if do_parseactions: LimitOffsetClauses_p.setName('LimitOffsetClauses').setParseAction(parseInfoFunc((LimitOffsetClauses)))

# [24]    OrderCondition    ::=   ( ( 'ASC' | 'DESC' ) BrackettedExpression ) | ( Constraint | Var ) 
OrderCondition_p =   Group((ASC_kw_p | DESC_kw_p) + BracketedExpression_p) | (Constraint_p | Var_p)
class OrderCondition(NonTerminal_): pass
if do_parseactions: OrderCondition_p.setName('OrderCondition').setParseAction(parseInfoFunc((OrderCondition)))

# [23]    OrderClause       ::=   'ORDER' 'BY' OrderCondition+ 
OrderClause_p = Group(ORDER_BY_kw_p + OneOrMore(OrderCondition_p) )
class OrderClause(NonTerminal_): pass
if do_parseactions: OrderClause_p.setName('OrderClause').setParseAction(parseInfoFunc((OrderClause)))

# [22]    HavingCondition   ::=   Constraint 
HavingCondition_p = Group(Constraint_p)
class HavingCondition(NonTerminal_): pass
if do_parseactions: HavingCondition_p.setName('HavingCondition').setParseAction(parseInfoFunc((HavingCondition)))

# [21]    HavingClause      ::=   'HAVING' HavingCondition+ 
HavingClause_p = Group(HAVING_kw_p + OneOrMore(HavingCondition_p) )
class HavingClause(NonTerminal_): pass
if do_parseactions: HavingClause_p.setName('HavingClause').setParseAction(parseInfoFunc((HavingClause)))

# [20]    GroupCondition    ::=   BuiltInCall | FunctionCall | '(' Expression ( 'AS' Var )? ')' | Var 
GroupCondition_p = Group(BuiltInCall_p | FunctionCall_p | (LPAR_p + Expression_p + Optional(AS_kw_p + Var_p) + RPAR_p) | Var_p )
class GroupCondition(NonTerminal_): pass
if do_parseactions: GroupCondition_p.setName('GroupCondition').setParseAction(parseInfoFunc((GroupCondition)))

# [19]    GroupClause       ::=   'GROUP' 'BY' GroupCondition+ 
GroupClause_p = Group(GROUP_BY_kw_p + OneOrMore(GroupCondition_p) )
class GroupClause(NonTerminal_): pass
if do_parseactions: GroupClause_p.setName('GroupClause').setParseAction(parseInfoFunc((GroupClause)))

# [18]    SolutionModifier          ::=   GroupClause? HavingClause? OrderClause? LimitOffsetClauses? 
SolutionModifier_p = Group(  Optional(GroupClause_p) + Optional(HavingClause_p) + Optional(OrderClause_p) + Optional(LimitOffsetClauses_p) )
class SolutionModifier(NonTerminal_): pass
if do_parseactions: SolutionModifier_p.setName('SolutionModifier').setParseAction(parseInfoFunc((SolutionModifier)))

# [17]    WhereClause       ::=   'WHERE'? GroupGraphPattern 
WhereClause_p = Group(  Optional(WHERE_kw_p) + GroupGraphPattern_p )
class WhereClause(NonTerminal_): pass
if do_parseactions: WhereClause_p.setName('WhereClause').setParseAction(parseInfoFunc((WhereClause)))

# [16]    SourceSelector    ::=   iri 
SourceSelector_p = Group(iri_p)
class SourceSelector(NonTerminal_): pass
if do_parseactions: SourceSelector_p.setName('SourceSelector').setParseAction(parseInfoFunc((SourceSelector)))

# [15]    NamedGraphClause          ::=   'NAMED' SourceSelector 
NamedGraphClause_p = Group(NAMED_kw_p + SourceSelector_p )
class NamedGraphClause(NonTerminal_): pass
if do_parseactions: NamedGraphClause_p.setName('NamedGraphClause').setParseAction(parseInfoFunc((NamedGraphClause)))

# [14]    DefaultGraphClause        ::=   SourceSelector 
DefaultGraphClause_p = Group(SourceSelector_p)
class DefaultGraphClause(NonTerminal_): pass
if do_parseactions: DefaultGraphClause_p.setName('DefaultGraphClause').setParseAction(parseInfoFunc((DefaultGraphClause)))

# [13]    DatasetClause     ::=   'FROM' ( DefaultGraphClause | NamedGraphClause ) 
DatasetClause_p = Group(FROM_kw_p + (DefaultGraphClause_p | NamedGraphClause_p) )
class DatasetClause(NonTerminal_): pass
if do_parseactions: DatasetClause_p.setName('DatasetClause').setParseAction(parseInfoFunc((DatasetClause)))

# [12]    AskQuery          ::=   'ASK' DatasetClause* WhereClause SolutionModifier 
AskQuery_p = Group(  ASK_kw_p + ZeroOrMore(DatasetClause_p) + WhereClause_p + SolutionModifier_p )
class AskQuery(NonTerminal_): pass
if do_parseactions: AskQuery_p.setName('AskQuery').setParseAction(parseInfoFunc((AskQuery)))

# [11]    DescribeQuery     ::=   'DESCRIBE' ( VarOrIri+ | '*' ) DatasetClause* WhereClause? SolutionModifier 
DescribeQuery_p = Group(DESCRIBE_kw_p + (OneOrMore(VarOrIri_p) | ALL_VALUES_st_p) + ZeroOrMore(DatasetClause_p) + Optional(WhereClause_p) + SolutionModifier_p )
class DescribeQuery(NonTerminal_): pass
if do_parseactions: DescribeQuery_p.setName('DescribeQuery').setParseAction(parseInfoFunc((DescribeQuery)))

# [10]    ConstructQuery    ::=   'CONSTRUCT' ( ConstructTemplate DatasetClause* WhereClause SolutionModifier | DatasetClause* 'WHERE' '{' TriplesTemplate? '}' SolutionModifier ) 
ConstructQuery_p = Group(CONSTRUCT_kw_p + ( (ConstructTemplate_p + ZeroOrMore(DatasetClause_p) + WhereClause_p + SolutionModifier_p) | \
                                      (ZeroOrMore(DatasetClause_p) + WHERE_kw_p + LCURL_p +  Optional(TriplesTemplate_p) + RCURL_p + SolutionModifier_p) ) )
class ConstructQuery(NonTerminal_): pass
if do_parseactions: ConstructQuery_p.setName('ConstructQuery').setParseAction(parseInfoFunc((ConstructQuery)))

# [9]     SelectClause      ::=   'SELECT' ( 'DISTINCT' | 'REDUCED' )? ( ( Var | ( '(' Expression 'AS' Var ')' ) )+ | '*' ) 
SelectClause_p = Group(SELECT_kw_p + Optional(DISTINCT_kw_p | REDUCED_kw_p) + ( OneOrMore(Var_p | (LPAR_p + Expression_p + AS_kw_p + Var_p + RPAR_p)) | ALL_VALUES_st_p ) )
class SelectClause(NonTerminal_): pass
if do_parseactions: SelectClause_p.setName('SelectClause').setParseAction(parseInfoFunc((SelectClause)))

# [8]     SubSelect         ::=   SelectClause WhereClause SolutionModifier ValuesClause 
SubSelect_p << Group(SelectClause_p + WhereClause_p + SolutionModifier_p + ValuesClause_p) 

# [7]     SelectQuery       ::=   SelectClause DatasetClause* WhereClause SolutionModifier 
SelectQuery_p = Group(SelectClause_p + ZeroOrMore(DatasetClause_p) + WhereClause_p + SolutionModifier_p )
class SelectQuery(NonTerminal_): pass
if do_parseactions: SelectQuery_p.setName('SelectQuery').setParseAction(parseInfoFunc((SelectQuery)))

# [6]     PrefixDecl        ::=   'PREFIX' PNAME_NS IRIREF 
PrefixDecl_p = Group(PREFIX_kw_p + PNAME_NS_p + IRIREF_p )
class PrefixDecl(NonTerminal_): pass
if do_parseactions: PrefixDecl_p.setName('PrefixDecl').setParseAction(parseInfoFunc((PrefixDecl)))

# [5]     BaseDecl          ::=   'BASE' IRIREF 
BaseDecl_p = Group(BASE_kw_p + IRIREF_p )
class BaseDecl(NonTerminal_): pass
if do_parseactions: BaseDecl_p.setName('BaseDecl').setParseAction(parseInfoFunc((BaseDecl)))

# [4]     Prologue          ::=   ( BaseDecl | PrefixDecl )* 
Prologue_p << Group(ZeroOrMore(BaseDecl_p | PrefixDecl_p)) 

# [3]     UpdateUnit        ::=   Update 
UpdateUnit_p = Group(Update_p )
class UpdateUnit(NonTerminal_): pass
if do_parseactions: UpdateUnit_p.setName('UpdateUnit').setParseAction(parseInfoFunc((UpdateUnit)))

# [2]     Query     ::=   Prologue ( SelectQuery | ConstructQuery | DescribeQuery | AskQuery ) ValuesClause 
Query_p = Group(Prologue_p + ( SelectQuery_p | ConstructQuery_p | DescribeQuery_p | AskQuery_p ) + ValuesClause_p )
class Query(NonTerminal_): pass
if do_parseactions: Query_p.setName('Query').setParseAction(parseInfoFunc((Query)))

# [1]     QueryUnit         ::=   Query 
QueryUnit_p = Group(Query_p)
class QueryUnit(NonTerminal_): pass
if do_parseactions: QueryUnit_p.setName('QueryUnit').setParseAction(parseInfoFunc((QueryUnit)))

'''
Created on 29 apr. 2016

@author: jeroenbruijning
'''
from pyparsing import *
from parsertools.base import ParseStruct, parseStructFunc, separatedList
from parsertools import ParsertoolsException, NoPrefixError
import re

# Custom exception. This is optional when defining a N3Parser. When present, it can be used in methods of the Parser class as defined below.

class N3ParseException(ParsertoolsException):
    '''Custom exception. This is optional when defining a N3Parser. When present, it can be used in methods of a ParseStruct subclass if
    defined below.'''
    
    pass

#
# Define the N3Element class
#

class N3Element(ParseStruct):
    '''Optional subclass of ParseStruct for the language. Typically, this class contains attributes and methods for the language that
    go beyond context free parsing, such as pre- and post processing, checking for conditions not covered by the grammar, etc.'''
    
    pass
#     def __init__(self, expr, base='', postCheck=True):
#         '''This constructor has an optional argument "base". This is the externally determined base iri, as per SPARQL definition par. 4.1.1.2.
#         It is only applied when the constructor is called with a string as expression to be parsed. (For internal bootstrapping purposes,
#         the constructor can also be called with expr equal to "None". See also the documentation for the ParseStruct constructor.)'''
#         ParseStruct.__init__(self, expr)
#         self.__dict__['_prefixes'] = {}
#         self.__dict__['_baseiri'] = None
#         if not expr is None:
#             self._applyPrefixesAndBase(baseiri=base)
#             if postCheck:
#                 self._checkParsedQuery()
#                     
#     def _applyPrefixesAndBase(self, prefixes={}, baseiri=None, isexternalbase=True):
#         '''Recursively attaches information to the element about the prefixes and base-iri valid at this point
#         in the expression, as determined by PREFIX and BASE declarations in the query.
#         The parameter isexternalbase is True when there is not yet a BASE declaration in force, as per the Turtle
#         specification. This indicates that the provided baseiri is externally determined, and should be overridden
#         by the first BASE declaration encountered (if any).
#         The first BASE declaration thus will replaces the externally determined base iri, instead
#         of being appended to it, which is what happens with subsequent BASE declarations.
#         Successful termination of this method does not guarantee that the base and prefixes conform to RFC 3987.
#         This is purely a syntactic (substitution) operation. Use other available tests to check BASE declarations and iri
#         expansion for conformance once this method has run.'''
#         
#         self.__dict__['_prefixes'] = prefixes
#         self.__dict__['_baseiri'] = baseiri
#         prefixes = prefixes.copy()
#         for elt in self.getChildren():
#             if isinstance(elt, N3Parser.Prologue):
#                 for decl in elt.getChildren():
#                     if isinstance(decl, N3Parser.PrefixDecl):
#                         assert str(decl.prefix) not in prefixes, 'Prefixes: {}, prefix: {}'.format(prefixes, decl.prefix)
#                         prefixes[str(decl.prefix)] = str(decl.namespace)[1:-1]
#                     else:
#                         assert isinstance(decl, N3Parser.BaseDecl)
#                         if isexternalbase or not baseiri:
#                             baseiri = str(decl.baseiri)[1:-1]
#                             isexternalbase = False
#                         else:
#                             baseiri = baseiri + str(decl.baseiri)[1:-1]
#                             
#             elt._applyPrefixesAndBase(prefixes, baseiri, isexternalbase)
#             
#     def getPrefixes(self):
#         return self._prefixes
#     
#     def getBaseiri(self):
#         return self._baseiri   
#         
#     def expandIris(self):
#         '''Converts all contained iri elements to normal form, taking into account the prefixes and base in force at the location of the iri.
#         The expansions are performed in place.'''
#         for elt in self.searchElements(element_type=N3Parser.iri):
#             children = elt.getChildren()
#             assert len(children) == 1, children
#             child = children[0]
# #             newiriref = '<' + getExpansion(str(child), elt._prefixes, elt._baseiri) + '>'
#             newiriref = '<' + getExpansion(child) + '>'
#             elt.updateWith(newiriref)
#             
#     def processEscapeSeqs(self):
#         for stringtype in [N3Parser.STRING_LITERAL2, N3Parser.STRING_LITERAL1, N3Parser.STRING_LITERAL_LONG1, N3Parser.STRING_LITERAL_LONG2]:
#             for elt in self.searchElements(element_type=stringtype):
#                 elt.updateWith(stringEscape(str(elt)))
# 
#     def _checkParsedQuery(self):
#         '''Used to perform additional checks on the ParseStruct resulting from a parsing action. These are conditions that are not covered by the EBNF syntax.
#         See the applicable comments and remarks in https://www.w3.org/TR/sparql11-query/, sections 19.1 - 19.8.'''
#         
#         # See 19.5 "IRI References"
#         self._checkBaseDecls()
#         self._checkIriExpansion()
#     #  TODO: finish
#                     
#     def _checkBaseDecls(self):
#         for elt in self.searchElements(element_type=N3Parser.BaseDecl):
#             rfc3987.parse(str(elt.baseiri)[1:-1], rule='absolute_IRI')
#     
#     def _checkIriExpansion(self):
#         '''Checks if all IRIs, after prefix processing and expansion, conform to RFC3987'''
#         for iri in self.searchElements(element_type=N3Parser.iri):
#             expanded = getExpansion(iri)
#             try:
#                 rfc3987.parse(expanded)
#             except ValueError as e:
#                 raise N3ParseException(str(e))  

#
# The following is boilerplate code, to be included in every Parsertools parser definition module
#

class Parser:
    '''Class to be instantiated to contain a parser for the language being implemented.
    This code must be present in the parser definition file for the language.
    Optionally, it takes a class argument if the language demands functionality in its
    ParseStruct elements that goes beyond what is provided in base.py. The argument must be
    a subclass of ParseStruct. The default is to instantiate the parser as a ParseStruct 
    parser.'''
    
    def __init__(self, class_=ParseStruct):
        self.class_ = class_
    def addElement(self, pattern, newclass=None):
        if newclass:
            assert issubclass(newclass, self.__class)
        else:
            newclass = self.class_ 
        setattr(self, pattern.name, type(pattern.name, (newclass,), {'_pattern': pattern}))
        pattern.setParseAction(parseStructFunc(getattr(self, pattern.name)))

#
# Create the N3Parser object, optionally with a custom ParseStruct subclass
#

N3Parser = Parser(N3Element)

# #
# # Main function to call. This is a convenience function, adapted to the SPARQL definition.
# #
# 
# def parseQuery(querystring, base=''):
#     '''Entry point to parse any SPARQL query'''
#     
#     s = prepareQuery(querystring)
#     
#     # In SPARQL, there are two entry points to the grammar: QueryUnit and UpdateUnit. These are tried in order.
#     
#     try:
#         result = N3Parser.QueryUnit(s, base=base)
#     except ParseException:
#         try:
#             result = N3Parser.UpdateUnit(s, base=base)
#         except ParseException:
#             raise N3ParseException('Query {} cannot be parsed'.format(querystring))
#         
#     result.processEscapeSeqs()    
#     
#     return result
# 
# #
# # Utility functions for SPARQL
# #
# 
# def prepareQuery(querystring):
#     '''Used to prepare a string for parsing. See the applicable comments and remarks in https://www.w3.org/TR/sparql11-query/, sections 19.1 - 19.8.'''
#     # See 19.4 "Comments"
#     querystring = stripComments(querystring)
#     # See 19.2 "Codepoint Escape Sequences"
#     querystring = unescapeUcode(querystring)
#     return querystring
# 
# 
# def stripComments(text):
#     '''Strips SPARQL-style comments from a multiline string'''
#     if isinstance(text, list):
#         text = '\n'.join(text)
#     Comment = Literal('#') + SkipTo(lineEnd)
#     NormalText = Regex('[^#<\'"]+')    
#     Line = ZeroOrMore(String | (IRIREF | Literal('<')) | NormalText) + Optional(Comment) + lineEnd
#     Line.ignore(Comment)
#     Line.setParseAction(lambda tokens: ' '.join([t if isinstance(t, str) else t.__str__() for t in tokens]))
#     lines = text.split('\n')
#     return '\n'.join([Line.parseString(l)[0] for l in lines])
# 
# def unescapeUcode(s):
#     
#     def escToUcode(s):
#         assert (s[:2] == r'\u' and len(s) == 6) or (s[:2] == r'\U' and len(s) == 10)
#         return chr(int(s[2:], 16))
#                    
#     smallUcodePattern = r'\\u[0-9a-fA-F]{4}'
#     largeUcodePattern = r'\\U[0-9a-fA-F]{8}'
#     s = re.sub(smallUcodePattern, lambda x: escToUcode(x.group()), s)
#     s = re.sub(largeUcodePattern, lambda x: escToUcode(x.group()), s)  
#       
#     return s
# 
# # helper function to determing the expanded form of an iri, in a given context of prefixes and base-iri.
#     
# # def getExpansion(iri, prefixes, baseiri):
# def getExpansion(iri):
#     '''Converts iri to normal form by replacing prefixes, if any, with their value and resolving the result, if relative, to absolute form.'''
#     assert isinstance(iri, (N3Parser.iri, N3Parser.PrefixedName, N3Parser.IRIREF)), 'Cannot expand non-iri element "{}" ({})'.format(iri, iri.__class__.__name__)        
#     if isinstance(iri, N3Parser.iri):
#         children = iri.getChildren()
#         assert len(children) == 1
#         oldiri = children[0]
#     else:
#         oldiri = iri
#     if isinstance(oldiri, N3Parser.PrefixedName):
#         splitiri = str(oldiri).split(':', maxsplit=1)
#         assert len(splitiri) == 2, splitiri
#         if splitiri[0] != '':
#             newiristr = oldiri.getPrefixes()[splitiri[0] + ':'][1:-1] + splitiri[1]
#         else:
#             newiristr = splitiri[1]
#     else:
#         assert isinstance(oldiri, N3Parser.IRIREF)
#         newiristr = str(oldiri)[1:-1]
#     if rfc3987.match(newiristr, 'irelative_ref'):
#         assert oldiri.getBaseiri() != None
#         newiristr = rfc3987.resolve(oldiri.getBaseiri(), newiristr)
#     assert rfc3987.match(newiristr), 'String "{}" cannot be expanded as absolute iri'.format(newiristr)
#     return newiristr
# 
#     
#     
# def stringEscape(s):
#     s = s.replace(r'\t', '\u0009')   
#     s = s.replace(r'\n', '\u000A')   
#     s = s.replace(r'\r', '\u000D')   
#     s = s.replace(r'\b', '\u0008')   
#     s = s.replace(r'\f', '\u000C')   
#     s = s.replace(r'\"', '\u0022')   
#     s = s.replace(r"\'", '\u0027')   
#     s = s.replace(r'\\', '\u005C')
#     return s

#
# Patterns
#

#
# Brackets and interpunction
#

# LPAR = Literal('(').setName('LPAR')
# N3Parser.addElement(LPAR)



#
# Operators
#

# NEGATE = Literal('!').setName('NEGATE')
# N3Parser.addElement(NEGATE)


#
# Keywords
#

# ALL_VALUES = Literal('*').setName('ALL_VALUES')
# N3Parser.addElement(ALL_VALUES)

# 
# Parsers and classes for terminals
#

# unsignedint ::=    [0-9]+
UNSIGNEDINT_e = r'[0-9]+'
UNSIGNEDINT = Regex(UNSIGNEDINT_e).setName('UNSIGNEDINT')
N3Parser.addElement(UNSIGNEDINT)

# langcode ::=    [a-z]+(-[a-z0-9]+)*
LANGCODE_e = r'[a-z]+(-[a-z0-9]+)*'
LANGCODE = Regex(LANGCODE_e).setName('LANGCODE')
N3Parser.addElement(LANGCODE)



#
# Parsers and classes for non-terminals
#

# # [138]   BlankNode         ::=   BLANK_NODE_LABEL | ANON 
# BlankNode = Group(BLANK_NODE_LABEL | ANON).setName('BlankNode')
# N3Parser.addElement(BlankNode)


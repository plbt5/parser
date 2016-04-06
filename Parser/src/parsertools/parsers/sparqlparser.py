'''
Created on 28 mrt. 2016

@author: jeroenbruijning
'''
from pyparsing import *
from parsertools.extras import separatedList
from parsertools.base import Parser
from parsertools import ParsertoolsException

#
# Main function to call. This is a convenience function, adapted to the SPARQL definition.
#

def parseQuery(querystring):
    '''Entry point to parse any SPARQL query'''
    

    
    s = prepareQuery(querystring)
    
    # In SPARQL, there are two entry points to the grammar: QueryUnit and UpdateUnit. These are tried in order.
    
    try:
        result = parser.QueryUnit(s)
    except ParseException:
        try:
            result = parser.UpdateUnit(s)
        except ParseException:
            raise ParsertoolsException('Query {} cannot be parsed'.format(querystring))
        
    assert checkQueryResult(result), 'Fault in postprocessing query {}'.format(querystring)
    
    return result

#
# Utility functions
#

def stripComments(text):
    '''Strips SPARQL-style comments from a multiline string'''
    if isinstance(text, list):
        text = '\n'.join(text)
    Comment = Literal('#') + SkipTo(lineEnd)
    NormalText = Regex('[^#<\'"]+')    
    Line = ZeroOrMore(String | (IRIREF | Literal('<')) | NormalText) + Optional(Comment) + lineEnd
    Line.ignore(Comment)
    Line.setParseAction(lambda tokens: ' '.join([t if isinstance(t, str) else t.__str__() for t in tokens]))
    lines = text.split('\n')
    return '\n'.join([Line.parseString(l)[0] for l in lines])

def prepareQuery(querystring):
    '''Used to prepare a string for parsing. See the applicable comments and remarks in https://www.w3.org/TR/sparql11-query/, sections 19.1 - 19.8.'''
    strippedQuery = stripComments(querystring)
    # TODO: finish
    return strippedQuery

def checkQueryResult(r):
    '''Used to perform additional checks on the parse result. These are conditions that are not covered by the EBNF syntax.
    See the applicable comments and remarks in https://www.w3.org/TR/sparql11-query/, sections 19.1 - 19.8.'''
    #TODO: finish
    return True

#
# Create the parser object
#

parser = Parser()

#
# Patterns
#

#
# Brackets and interpunction
#


LPAR = Literal('(').setName('LPAR')
parser.addElement(LPAR)

RPAR = Literal(')').setName('RPAR')
parser.addElement(RPAR)

LBRACK = Literal('[').setName('LBRACK')
parser.addElement(LBRACK)

RBRACK = Literal(']').setName('RBRACK')
parser.addElement(RBRACK)

LCURL = Literal('{').setName('LCURL')
parser.addElement(LCURL)

RCURL = Literal('}').setName('RCURL')
parser.addElement(RCURL)

SEMICOL = Literal(';').setName('SEMICOL')
parser.addElement(SEMICOL)

PERIOD = Literal('.').setName('PERIOD')
parser.addElement(PERIOD)

COMMA = Literal(',').setName('COMMA')
parser.addElement(COMMA)

#
# Operators
#

NEGATE = Literal('!').setName('NEGATE')
parser.addElement(NEGATE)

PLUS = Literal('+').setName('PLUS')
parser.addElement(PLUS)

MINUS = Literal('-').setName('MINUS')
parser.addElement(MINUS)

TIMES = Literal('*').setName('TIMES')
parser.addElement(TIMES)

DIV = Literal('/').setName('DIV')
parser.addElement(DIV)

EQ = Literal('=').setName('EQ')
parser.addElement(EQ)

NE = Literal('!=').setName('NE')
parser.addElement(NE)

GT = Literal('>').setName('GT')
parser.addElement(GT)

LT = Literal('<').setName('LT')
parser.addElement(LT)

GE = Literal('>=').setName('GE')
parser.addElement(GE)

LE = Literal('<=').setName('LE')
parser.addElement(LE)

AND = Literal('&&').setName('AND')
parser.addElement(AND)

OR = Literal('||').setName('OR')
parser.addElement(OR)

INVERSE = Literal('^').setName('INVERSE')
parser.addElement(INVERSE)

#
# Keywords
#

ALL_VALUES = Literal('*').setName('ALL_VALUES')
parser.addElement(ALL_VALUES)

TYPE = Keyword('a').setName('TYPE')
parser.addElement(TYPE)

DISTINCT = CaselessKeyword('DISTINCT').setName('DISTINCT')
parser.addElement(DISTINCT)

COUNT = CaselessKeyword('COUNT').setName('COUNT')
parser.addElement(COUNT)

SUM = CaselessKeyword('SUM').setName('SUM')
parser.addElement(SUM)

MIN = CaselessKeyword('MIN').setName('MIN')
parser.addElement(MIN)

MAX = CaselessKeyword('MAX').setName('MAX')
parser.addElement(MAX)

AVG = CaselessKeyword('AVG').setName('AVG')
parser.addElement(AVG)

SAMPLE = CaselessKeyword('SAMPLE').setName('SAMPLE')
parser.addElement(SAMPLE)

GROUP_CONCAT = CaselessKeyword('GROUP_CONCAT').setName('GROUP_CONCAT')
parser.addElement(GROUP_CONCAT)

SEPARATOR = CaselessKeyword('SEPARATOR').setName('SEPARATOR')
parser.addElement(SEPARATOR)

NOT = (CaselessKeyword('NOT') + NotAny(CaselessKeyword('EXISTS') | CaselessKeyword('IN'))).setName('NOT')
parser.addElement(NOT)

EXISTS = CaselessKeyword('EXISTS').setName('EXISTS')
parser.addElement(EXISTS)

NOT_EXISTS = (CaselessKeyword('NOT') + CaselessKeyword('EXISTS')).setName('NOT_EXISTS')
parser.addElement(NOT_EXISTS)

REPLACE = CaselessKeyword('REPLACE').setName('REPLACE')
parser.addElement(REPLACE)

SUBSTR = CaselessKeyword('SUBSTR').setName('SUBSTR')
parser.addElement(SUBSTR)

REGEX = CaselessKeyword('REGEX').setName('REGEX')
parser.addElement(REGEX)

STR = CaselessKeyword('STR').setName('STR')
parser.addElement(STR)

LANG = CaselessKeyword('LANG').setName('LANG')
parser.addElement(LANG)

LANGMATCHES = CaselessKeyword('LANGMATCHES').setName('LANGMATCHES')
parser.addElement(LANGMATCHES)

DATATYPE = CaselessKeyword('DATATYPE').setName('DATATYPE')
parser.addElement(DATATYPE)

BOUND = CaselessKeyword('BOUND').setName('BOUND')
parser.addElement(BOUND)

IRI = CaselessKeyword('IRI').setName('IRI')
parser.addElement(IRI)

URI = CaselessKeyword('URI').setName('URI')
parser.addElement(URI)

BNODE = CaselessKeyword('BNODE').setName('BNODE')
parser.addElement(BNODE)

RAND = CaselessKeyword('RAND').setName('RAND')
parser.addElement(RAND)

ABS = CaselessKeyword('ABS').setName('ABS')
parser.addElement(ABS)

CEIL = CaselessKeyword('CEIL').setName('CEIL')
parser.addElement(CEIL)

FLOOR = CaselessKeyword('FLOOR').setName('FLOOR')
parser.addElement(FLOOR)

ROUND = CaselessKeyword('ROUND').setName('ROUND')
parser.addElement(ROUND)

CONCAT = CaselessKeyword('CONCAT').setName('CONCAT')
parser.addElement(CONCAT)

STRLEN = CaselessKeyword('STRLEN').setName('STRLEN')
parser.addElement(STRLEN)

UCASE = CaselessKeyword('UCASE').setName('UCASE')
parser.addElement(UCASE)

LCASE = CaselessKeyword('LCASE').setName('LCASE')
parser.addElement(LCASE)

ENCODE_FOR_URI = CaselessKeyword('ENCODE_FOR_URI').setName('ENCODE_FOR_URI')
parser.addElement(ENCODE_FOR_URI)

CONTAINS = CaselessKeyword('CONTAINS').setName('CONTAINS')
parser.addElement(CONTAINS)

STRSTARTS = CaselessKeyword('STRSTARTS').setName('STRSTARTS')
parser.addElement(STRSTARTS)

STRENDS = CaselessKeyword('STRENDS').setName('STRENDS')
parser.addElement(STRENDS)

STRBEFORE = CaselessKeyword('STRBEFORE').setName('STRBEFORE')
parser.addElement(STRBEFORE)

STRAFTER = CaselessKeyword('STRAFTER').setName('STRAFTER')
parser.addElement(STRAFTER)

YEAR = CaselessKeyword('YEAR').setName('YEAR')
parser.addElement(YEAR)

MONTH = CaselessKeyword('MONTH').setName('MONTH')
parser.addElement(MONTH)

DAY = CaselessKeyword('DAY').setName('DAY')
parser.addElement(DAY)

HOURS = CaselessKeyword('HOURS').setName('HOURS')
parser.addElement(HOURS)

MINUTES = CaselessKeyword('MINUTES').setName('MINUTES')
parser.addElement(MINUTES)

SECONDS = CaselessKeyword('SECONDS').setName('SECONDS')
parser.addElement(SECONDS)

TIMEZONE = CaselessKeyword('TIMEZONE').setName('TIMEZONE')
parser.addElement(TIMEZONE)

TZ = CaselessKeyword('TZ').setName('TZ')
parser.addElement(TZ)

NOW = CaselessKeyword('NOW').setName('NOW')
parser.addElement(NOW)

UUID = CaselessKeyword('UUID').setName('UUID')
parser.addElement(UUID)

STRUUID = CaselessKeyword('STRUUID').setName('STRUUID')
parser.addElement(STRUUID)

MD5 = CaselessKeyword('MD5').setName('MD5')
parser.addElement(MD5)

SHA1 = CaselessKeyword('SHA1').setName('SHA1')
parser.addElement(SHA1)

SHA256 = CaselessKeyword('SHA256').setName('SHA256')
parser.addElement(SHA256)

SHA384 = CaselessKeyword('SHA384').setName('SHA384')
parser.addElement(SHA384)

SHA512 = CaselessKeyword('SHA512').setName('SHA512')
parser.addElement(SHA512)

COALESCE = CaselessKeyword('COALESCE').setName('COALESCE')
parser.addElement(COALESCE)

IF = CaselessKeyword('IF').setName('IF')
parser.addElement(IF)

STRLANG = CaselessKeyword('STRLANG').setName('STRLANG')
parser.addElement(STRLANG)

STRDT = CaselessKeyword('STRDT').setName('STRDT')
parser.addElement(STRDT)

sameTerm = CaselessKeyword('sameTerm').setName('sameTerm')
parser.addElement(sameTerm)

isIRI = CaselessKeyword('isIRI').setName('isIRI')
parser.addElement(isIRI)

isURI = CaselessKeyword('isURI').setName('isURI')
parser.addElement(isURI)

isBLANK = CaselessKeyword('isBLANK').setName('isBLANK')
parser.addElement(isBLANK)

isLITERAL = CaselessKeyword('isLITERAL').setName('isLITERAL')
parser.addElement(isLITERAL)

isNUMERIC = CaselessKeyword('isNUMERIC').setName('isNUMERIC')
parser.addElement(isNUMERIC)

IN = CaselessKeyword('IN').setName('IN')
parser.addElement(IN)

NOT_IN = (CaselessKeyword('NOT') + CaselessKeyword('IN')).setName('NOT_IN')
parser.addElement(NOT_IN)

FILTER = CaselessKeyword('FILTER').setName('FILTER')
parser.addElement(FILTER)

UNION = CaselessKeyword('UNION').setName('UNION')
parser.addElement(UNION)

SUBTRACT = CaselessKeyword('MINUS').setName('SUBTRACT')
parser.addElement(SUBTRACT)

UNDEF = CaselessKeyword('UNDEF').setName('UNDEF')
parser.addElement(UNDEF)

VALUES = CaselessKeyword('VALUES').setName('VALUES')
parser.addElement(VALUES)

BIND = CaselessKeyword('BIND').setName('BIND')
parser.addElement(BIND)

AS = CaselessKeyword('AS').setName('AS')
parser.addElement(AS)

SERVICE = CaselessKeyword('SERVICE').setName('SERVICE')
parser.addElement(SERVICE)

SILENT = CaselessKeyword('SILENT').setName('SILENT')
parser.addElement(SILENT)

GRAPH = CaselessKeyword('GRAPH').setName('GRAPH')
parser.addElement(GRAPH)

OPTIONAL = CaselessKeyword('OPTIONAL').setName('OPTIONAL')
parser.addElement(OPTIONAL)

DEFAULT = CaselessKeyword('DEFAULT').setName('DEFAULT')
parser.addElement(DEFAULT)

NAMED = CaselessKeyword('NAMED').setName('NAMED')
parser.addElement(NAMED)

ALL = CaselessKeyword('ALL').setName('ALL')
parser.addElement(ALL)

USING = CaselessKeyword('USING').setName('USING')
parser.addElement(USING)

INSERT = CaselessKeyword('INSERT').setName('INSERT')
parser.addElement(INSERT)

DELETE = CaselessKeyword('DELETE').setName('DELETE')
parser.addElement(DELETE)

WITH = CaselessKeyword('WITH').setName('WITH')
parser.addElement(WITH)

WHERE = CaselessKeyword('WHERE').setName('WHERE')
parser.addElement(WHERE)

DELETE_WHERE = (CaselessKeyword('DELETE') + CaselessKeyword('WHERE')).setName('DELETE_WHERE')
parser.addElement(DELETE_WHERE)

DELETE_DATA = (CaselessKeyword('DELETE') + CaselessKeyword('DATA')).setName('DELETE_DATA')
parser.addElement(DELETE_DATA)

INSERT_DATA = (CaselessKeyword('INSERT') + CaselessKeyword('DATA')).setName('INSERT_DATA')
parser.addElement(INSERT_DATA)

COPY = CaselessKeyword('COPY').setName('COPY')
parser.addElement(COPY)

MOVE = CaselessKeyword('MOVE').setName('MOVE')
parser.addElement(MOVE)

ADD = CaselessKeyword('ADD').setName('ADD')
parser.addElement(ADD)

CREATE = CaselessKeyword('CREATE').setName('CREATE')
parser.addElement(CREATE)

DROP = CaselessKeyword('DROP').setName('DROP')
parser.addElement(DROP)

CLEAR = CaselessKeyword('CLEAR').setName('CLEAR')
parser.addElement(CLEAR)

LOAD = CaselessKeyword('LOAD').setName('LOAD')
parser.addElement(LOAD)

TO = CaselessKeyword('TO').setName('TO')
parser.addElement(TO)

INTO = CaselessKeyword('INTO').setName('INTO')
parser.addElement(INTO)

OFFSET = CaselessKeyword('OFFSET').setName('OFFSET')
parser.addElement(OFFSET)

LIMIT = CaselessKeyword('LIMIT').setName('LIMIT')
parser.addElement(LIMIT)

ASC = CaselessKeyword('ASC').setName('ASC')
parser.addElement(ASC)

DESC = CaselessKeyword('DESC').setName('DESC')
parser.addElement(DESC)

ORDER_BY = (CaselessKeyword('ORDER') + CaselessKeyword('BY')).setName('ORDER_BY')
parser.addElement(ORDER_BY)

HAVING = CaselessKeyword('HAVING').setName('HAVING')
parser.addElement(HAVING)

GROUP_BY = (CaselessKeyword('GROUP') + CaselessKeyword('BY')).setName('GROUP_BY')
parser.addElement(GROUP_BY)

FROM = CaselessKeyword('FROM').setName('FROM')
parser.addElement(FROM)

ASK = CaselessKeyword('ASK').setName('ASK')
parser.addElement(ASK)

DESCRIBE = CaselessKeyword('DESCRIBE').setName('DESCRIBE')
parser.addElement(DESCRIBE)

CONSTRUCT = CaselessKeyword('CONSTRUCT').setName('CONSTRUCT')
parser.addElement(CONSTRUCT)

SELECT = CaselessKeyword('SELECT').setName('SELECT')
parser.addElement(SELECT)

REDUCED = CaselessKeyword('REDUCED').setName('REDUCED')
parser.addElement(REDUCED)

PREFIX = CaselessKeyword('PREFIX').setName('PREFIX')
parser.addElement(PREFIX)

BASE = CaselessKeyword('BASE').setName('BASE')
parser.addElement(BASE)

# 
# Parsers and classes for terminals
#

# [173]   PN_LOCAL_ESC      ::=   '\' ( '_' | '~' | '.' | '-' | '!' | '$' | '&' | "'" | '(' | ')' | '*' | '+' | ',' | ';' | '=' | '/' | '?' | '#' | '@' | '%' ) 
PN_LOCAL_ESC_e = r'\\[_~.\-!$&\'()*+,;=/?#@%]'
PN_LOCAL_ESC = Regex(PN_LOCAL_ESC_e).setName('PN_LOCAL_ESC')
parser.addElement(PN_LOCAL_ESC)


# [172]   HEX       ::=   [0-9] | [A-F] | [a-f] 
HEX_e = r'[0-9A-Fa-f]'
HEX = Regex(HEX_e).setName('HEX')
parser.addElement(HEX)

# [171]   PERCENT   ::=   '%' HEX HEX
PERCENT_e = r'%({})({})'.format( HEX_e, HEX_e)
PERCENT = Regex(PERCENT_e).setName('PERCENT')
parser.addElement(PERCENT)

# [170]   PLX       ::=   PERCENT | PN_LOCAL_ESC 
PLX_e = r'({})|({})'.format( PERCENT_e, PN_LOCAL_ESC_e)
PLX = Regex(PLX_e).setName('PLX')
parser.addElement(PLX)

# [164]   PN_CHARS_BASE     ::=   [A-Z] | [a-z] | [#x00C0-#x00D6] | [#x00D8-#x00F6] | [#x00F8-#x02FF] | [#x0370-#x037D] | [#x037F-#x1FFF] | [#x200C-#x200D] | [#x2070-#x218F] | [#x2C00-#x2FEF] | [#x3001-#xD7FF] | [#xF900-#xFDCF] | [#xFDF0-#xFFFD] | [#x10000-#xEFFFF] 
PN_CHARS_BASE_e = r'[A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\U00010000-\U000EFFFF]'
PN_CHARS_BASE = Regex(PN_CHARS_BASE_e).setName('PN_CHARS_BASE')
parser.addElement(PN_CHARS_BASE)

# [165]   PN_CHARS_U        ::=   PN_CHARS_BASE | '_' 
PN_CHARS_U_e = r'({})|({})'.format( PN_CHARS_BASE_e, r'_')
PN_CHARS_U = Regex(PN_CHARS_U_e).setName('PN_CHARS_U')
parser.addElement(PN_CHARS_U)

# [167]   PN_CHARS          ::=   PN_CHARS_U | '-' | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] 
PN_CHARS_e = r'({})|({})|({})|({})|({})|({})'.format( PN_CHARS_U_e, r'\-', r'[0-9]',  r'\u00B7', r'[\u0300-\u036F]', r'[\u203F-\u2040]')
PN_CHARS = Regex(PN_CHARS_e).setName('PN_CHARS')
parser.addElement(PN_CHARS)

# [169]   PN_LOCAL          ::=   (PN_CHARS_U | ':' | [0-9] | PLX ) ((PN_CHARS | '.' | ':' | PLX)* (PN_CHARS | ':' | PLX) )?
PN_LOCAL_e = r'(({})|({})|({})|({}))((({})|({})|({})|({}))*(({})|({})|({})))?'.format( PN_CHARS_U_e, r':', r'[0-9]', PLX_e, PN_CHARS_e, r'\.', r':', PLX_e, PN_CHARS_e, r':', PLX_e) 
PN_LOCAL = Regex(PN_LOCAL_e).setName('PN_LOCAL')
parser.addElement(PN_LOCAL)
            
# [168]   PN_PREFIX         ::=   PN_CHARS_BASE ((PN_CHARS|'.')* PN_CHARS)?
PN_PREFIX_e = r'({})((({})|({}))*({}))?'.format( PN_CHARS_BASE_e, PN_CHARS_e, r'\.', PN_CHARS_e)
PN_PREFIX = Regex(PN_PREFIX_e).setName('PN_PREFIX')
parser.addElement(PN_PREFIX)

# [166]   VARNAME   ::=   ( PN_CHARS_U | [0-9] ) ( PN_CHARS_U | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] )* 
VARNAME_e = r'(({})|({}))(({})|({})|({})|({})|({}))*'.format( PN_CHARS_U_e, r'[0-9]', PN_CHARS_U_e, r'[0-9]', r'\u00B7', r'[\u0030-036F]', r'[\u0203-\u2040]')
VARNAME = Regex(VARNAME_e).setName('VARNAME')
parser.addElement(VARNAME)

# [163]   ANON      ::=   '[' WS* ']' 
ANON = Group(Literal('[') + Literal(']')).setName('ANON')
parser.addElement(ANON)

# [162]   WS        ::=   #x20 | #x9 | #xD | #xA 
# WS is not used
# In the SPARQL EBNF this production is used for defining NIL and ANON, but in this pyparsing implementation those are implemented differently

# [161]   NIL       ::=   '(' WS* ')' 
NIL = Group(Literal('(') + Literal(')')).setName('NIL')
parser.addElement(NIL)

# [160]   ECHAR     ::=   '\' [tbnrf\"']
ECHAR_e = r'\\[tbnrf\\"\']'
ECHAR = Regex(ECHAR_e).setName('ECHAR')
parser.addElement(ECHAR)
 
# [159]   STRING_LITERAL_LONG2      ::=   '"""' ( ( '"' | '""' )? ( [^"\] | ECHAR ) )* '"""'  
STRING_LITERAL_LONG2_e = r'"""((""|")?(({})|({})))*"""'.format(r'[^"\\]', ECHAR_e)
STRING_LITERAL_LONG2 = Regex(STRING_LITERAL_LONG2_e).parseWithTabs().setName('STRING_LITERAL_LONG2')
parser.addElement(STRING_LITERAL_LONG2)

# [158]   STRING_LITERAL_LONG1      ::=   "'''" ( ( "'" | "''" )? ( [^'\] | ECHAR ) )* "'''" 
STRING_LITERAL_LONG1_e = r"'''(('|'')?(({})|({})))*'''".format(r"[^'\\]", ECHAR_e)
STRING_LITERAL_LONG1 = Regex(STRING_LITERAL_LONG1_e).parseWithTabs().setName('STRING_LITERAL_LONG1')
parser.addElement(STRING_LITERAL_LONG1)

# [157]   STRING_LITERAL2   ::=   '"' ( ([^#x22#x5C#xA#xD]) | ECHAR )* '"' 
STRING_LITERAL2_e = r'"(({})|({}))*"'.format(ECHAR_e, r'[^\u0022\u005C\u000A\u000D]')
STRING_LITERAL2 = Regex(STRING_LITERAL2_e).parseWithTabs().setName('STRING_LITERAL2')
parser.addElement(STRING_LITERAL2)
                           
# [156]   STRING_LITERAL1   ::=   "'" ( ([^#x27#x5C#xA#xD]) | ECHAR )* "'" 
STRING_LITERAL1_e = r"'(({})|({}))*'".format(ECHAR_e, r'[^\u0027\u005C\u000A\u000D]')
STRING_LITERAL1 = Regex(STRING_LITERAL1_e).parseWithTabs().setName('STRING_LITERAL1')
parser.addElement(STRING_LITERAL1)
                            
# [155]   EXPONENT          ::=   [eE] [+-]? [0-9]+ 
EXPONENT_e = r'[eE][+-][0-9]+'
EXPONENT = Regex(EXPONENT_e).setName('EXPONENT')
parser.addElement(EXPONENT)

# [148]   DOUBLE    ::=   [0-9]+ '.' [0-9]* EXPONENT | '.' ([0-9])+ EXPONENT | ([0-9])+ EXPONENT 
DOUBLE_e = r'([0-9]+\.[0-9]*({}))|(\.[0-9]+({}))|([0-9]+({}))'.format(EXPONENT_e, EXPONENT_e, EXPONENT_e)
DOUBLE = Regex(DOUBLE_e).setName('DOUBLE')
parser.addElement(DOUBLE)

# [154]   DOUBLE_NEGATIVE   ::=   '-' DOUBLE 
DOUBLE_NEGATIVE_e = r'\-({})'.format(DOUBLE_e)
DOUBLE_NEGATIVE = Regex(DOUBLE_NEGATIVE_e).setName('DOUBLE_NEGATIVE')
parser.addElement(DOUBLE_NEGATIVE)

# [151]   DOUBLE_POSITIVE   ::=   '+' DOUBLE 
DOUBLE_POSITIVE_e = r'\+({})'.format(DOUBLE_e)
DOUBLE_POSITIVE = Regex(DOUBLE_POSITIVE_e).setName('DOUBLE_POSITIVE')
parser.addElement(DOUBLE_POSITIVE)

# [147]   DECIMAL   ::=   [0-9]* '.' [0-9]+ 
DECIMAL_e = r'[0-9]*\.[0-9]+'
DECIMAL = Regex(DECIMAL_e).setName('DECIMAL')
parser.addElement(DECIMAL)

# [153]   DECIMAL_NEGATIVE          ::=   '-' DECIMAL 
DECIMAL_NEGATIVE_e = r'\-({})'.format(DECIMAL_e)
DECIMAL_NEGATIVE = Regex(DECIMAL_NEGATIVE_e).setName('DECIMAL_NEGATIVE')
parser.addElement(DECIMAL_NEGATIVE)

# [150]   DECIMAL_POSITIVE          ::=   '+' DECIMAL 
DECIMAL_POSITIVE_e = r'\+({})'.format(DECIMAL_e)
DECIMAL_POSITIVE = Regex(DECIMAL_POSITIVE_e).setName('DECIMAL_POSITIVE')
parser.addElement(DECIMAL_POSITIVE)

# [146]   INTEGER   ::=   [0-9]+ 
INTEGER_e = r'[0-9]+'
INTEGER = Regex(INTEGER_e).setName('INTEGER')
parser.addElement(INTEGER)

# [152]   INTEGER_NEGATIVE          ::=   '-' INTEGER
INTEGER_NEGATIVE_e = r'\-({})'.format(INTEGER_e)
INTEGER_NEGATIVE = Regex(INTEGER_NEGATIVE_e).setName('INTEGER_NEGATIVE')
parser.addElement(INTEGER_NEGATIVE)

# [149]   INTEGER_POSITIVE          ::=   '+' INTEGER 
INTEGER_POSITIVE_e = r'\+({})'.format(INTEGER_e)
INTEGER_POSITIVE = Regex(INTEGER_POSITIVE_e).setName('INTEGER_POSITIVE')
parser.addElement(INTEGER_POSITIVE)

# [145]   LANGTAG   ::=   '@' [a-zA-Z]+ ('-' [a-zA-Z0-9]+)* 
LANGTAG_e = r'@[a-zA-Z]+(\-[a-zA-Z0-9]+)*'
LANGTAG = Regex(LANGTAG_e).setName('LANGTAG')
parser.addElement(LANGTAG)

# [144]   VAR2      ::=   '$' VARNAME 
VAR2_e = r'\$({})'.format(VARNAME_e)
VAR2 = Regex(VAR2_e).setName('VAR2')
parser.addElement(VAR2)

# [143]   VAR1      ::=   '?' VARNAME 
VAR1_e = r'\?({})'.format(VARNAME_e)
VAR1 = Regex(VAR1_e).setName('VAR1')
parser.addElement(VAR1)

# [142]   BLANK_NODE_LABEL          ::=   '_:' ( PN_CHARS_U | [0-9] ) ((PN_CHARS|'.')* PN_CHARS)?
BLANK_NODE_LABEL_e = r'_:(({})|[0-9])((({})|\.)*({}))?'.format(PN_CHARS_U_e, PN_CHARS_e, PN_CHARS_e)
BLANK_NODE_LABEL = Regex(BLANK_NODE_LABEL_e).setName('BLANK_NODE_LABEL')
parser.addElement(BLANK_NODE_LABEL)

# [140]   PNAME_NS          ::=   PN_PREFIX? ':'
PNAME_NS_e = r'({})?:'.format(PN_PREFIX_e)
PNAME_NS = Regex(PNAME_NS_e).setName('PNAME_NS')
parser.addElement(PNAME_NS)

# [141]   PNAME_LN          ::=   PNAME_NS PN_LOCAL 
PNAME_LN_e = r'({})({})'.format(PNAME_NS_e, PN_LOCAL_e)
PNAME_LN = Regex(PNAME_LN_e).setName('PNAME_LN')
parser.addElement(PNAME_LN)

# [139]   IRIREF    ::=   '<' ([^<>"{}|^`\]-[#x00-#x20])* '>' 
IRIREF_e = r'<[^<>"{}|^`\\\\\u0000-\u0020]*>'
IRIREF = Regex(IRIREF_e).setName('IRIREF')
parser.addElement(IRIREF)

#
# Parsers and classes for non-terminals
#

# [138]   BlankNode         ::=   BLANK_NODE_LABEL | ANON 
BlankNode = Group(BLANK_NODE_LABEL | ANON).setName('BlankNode')
parser.addElement(BlankNode)

# [137]   PrefixedName      ::=   PNAME_LN | PNAME_NS 
PrefixedName = Group(PNAME_LN | PNAME_NS).setName('PrefixedName')
parser.addElement(PrefixedName)

# [136]   iri       ::=   IRIREF | PrefixedName 
iri = Group(IRIREF | PrefixedName).setName('iri')
parser.addElement(iri)

# [135]   String    ::=   STRING_LITERAL1 | STRING_LITERAL2 | STRING_LITERAL_LONG1 | STRING_LITERAL_LONG2 
String = Group(STRING_LITERAL_LONG1 | STRING_LITERAL_LONG2 | STRING_LITERAL1 | STRING_LITERAL2).setName('String')
parser.addElement(String)
 
# [134]   BooleanLiteral    ::=   'true' | 'false' 
BooleanLiteral = Group(Literal('true') | Literal('false')).setName('BooleanLiteral')
parser.addElement(BooleanLiteral)
 
# [133]   NumericLiteralNegative    ::=   INTEGER_NEGATIVE | DECIMAL_NEGATIVE | DOUBLE_NEGATIVE 
NumericLiteralNegative = Group(DOUBLE_NEGATIVE | DECIMAL_NEGATIVE | INTEGER_NEGATIVE).setName('NumericLiteralNegative')
parser.addElement(NumericLiteralNegative)
 
# [132]   NumericLiteralPositive    ::=   INTEGER_POSITIVE | DECIMAL_POSITIVE | DOUBLE_POSITIVE 
NumericLiteralPositive = Group(DOUBLE_POSITIVE | DECIMAL_POSITIVE | INTEGER_POSITIVE).setName('NumericLiteralPositive')
parser.addElement(NumericLiteralPositive)
 
# [131]   NumericLiteralUnsigned    ::=   INTEGER | DECIMAL | DOUBLE 
NumericLiteralUnsigned = Group(DOUBLE | DECIMAL | INTEGER).setName('NumericLiteralUnsigned')
parser.addElement(NumericLiteralUnsigned)

# # [130]   NumericLiteral    ::=   NumericLiteralUnsigned | NumericLiteralPositive | NumericLiteralNegative 
NumericLiteral = Group(NumericLiteralUnsigned | NumericLiteralPositive | NumericLiteralNegative).setName('NumericLiteral')
parser.addElement(NumericLiteral)

# [129]   RDFLiteral        ::=   String ( LANGTAG | ( '^^' iri ) )? 
RDFLiteral = Group(String('lexical_form') + Optional(Group ((LANGTAG('langtag') | ('^^' + iri('datatype_uri')))))).setName('RDFLiteral')
parser.addElement(RDFLiteral)

Expression = Forward().setName('Expression')
parser.addElement(Expression)

# [71]    ArgList   ::=   NIL | '(' 'DISTINCT'? Expression ( ',' Expression )* ')' 
ArgList = Group((NIL('nil')) | (LPAR + Optional(DISTINCT)('distinct') + separatedList(Expression)('argument') + RPAR)).setName('ArgList')
parser.addElement(ArgList)


# [128]   iriOrFunction     ::=   iri ArgList? 
iriOrFunction = Group(iri('iri') + Optional(ArgList)('argList')).setName('iriOrFunction')
parser.addElement(iriOrFunction)

# [127]   Aggregate         ::=     'COUNT' '(' 'DISTINCT'? ( '*' | Expression ) ')' 
#             | 'SUM' '(' 'DISTINCT'? Expression ')' 
#             | 'MIN' '(' 'DISTINCT'? Expression ')' 
#             | 'MAX' '(' 'DISTINCT'? Expression ')' 
#             | 'AVG' '(' 'DISTINCT'? Expression ')' 
#             | 'SAMPLE' '(' 'DISTINCT'? Expression ')' 
#             | 'GROUP_CONCAT' '(' 'DISTINCT'? Expression ( ';' 'SEPARATOR' '=' String )? ')' 
Aggregate = Group((COUNT('count') + LPAR + Optional(DISTINCT('distinct')) + ( ALL_VALUES('all') | Expression('expression') ) + RPAR ) | \
            ( SUM('sum') + LPAR + Optional(DISTINCT('distinct')) + ( ALL_VALUES('all') | Expression('expression') ) + RPAR ) | \
            ( MIN('min') + LPAR + Optional(DISTINCT('distinct')) + ( ALL_VALUES('all') | Expression('expression') ) + RPAR ) | \
            ( MAX('max') + LPAR + Optional(DISTINCT('distinct')) + ( ALL_VALUES('all') | Expression('expression') ) + RPAR ) | \
            ( AVG('avg') + LPAR + Optional(DISTINCT('distinct')) + ( ALL_VALUES('all') | Expression('expression') ) + RPAR ) | \
            ( SAMPLE('sample') + LPAR + Optional(DISTINCT('distinct')) + ( ALL_VALUES('all') | Expression('expression') ) + RPAR ) | \
            ( GROUP_CONCAT('group_concat') + LPAR + Optional(DISTINCT('distinct')) + Expression('expression') + Optional( SEMICOL + SEPARATOR + '=' + String('separator') ) + RPAR)).setName('Aggregate')
parser.addElement(Aggregate)

GroupGraphPattern = Forward().setName('GroupGraphPattern')
parser.addElement(GroupGraphPattern)
 
# [126]   NotExistsFunc     ::=   'NOT' 'EXISTS' GroupGraphPattern 
NotExistsFunc = Group(NOT_EXISTS + GroupGraphPattern('groupgraph')).setName('NotExistsFunc')
parser.addElement(NotExistsFunc)
 
# [125]   ExistsFunc        ::=   'EXISTS' GroupGraphPattern 
ExistsFunc = Group(EXISTS + GroupGraphPattern('groupgraph')).setName('ExistsFunc')
parser.addElement(ExistsFunc)
 
# [124]   StrReplaceExpression      ::=   'REPLACE' '(' Expression ',' Expression ',' Expression ( ',' Expression )? ')' 
StrReplaceExpression = Group(REPLACE + LPAR + Expression('arg') + COMMA + Expression('pattern') + COMMA + Expression('replacement') + Optional(COMMA + Expression('flags')) + RPAR).setName('StrReplaceExpression')
parser.addElement(StrReplaceExpression)
 
# [123]   SubstringExpression       ::=   'SUBSTR' '(' Expression ',' Expression ( ',' Expression )? ')' 
SubstringExpression = Group(SUBSTR + LPAR + Expression('source') + COMMA + Expression('startloc') + Optional(COMMA + Expression('length')) + RPAR).setName('SubstringExpression')
parser.addElement(SubstringExpression)
 
# [122]   RegexExpression   ::=   'REGEX' '(' Expression ',' Expression ( ',' Expression )? ')' 
RegexExpression = Group(REGEX + LPAR + Expression('text') + COMMA + Expression('pattern') + Optional(COMMA + Expression('flags')) + RPAR).setName('RegexExpression')
parser.addElement(RegexExpression)

# [108]   Var       ::=   VAR1 | VAR2 
Var = Group(VAR1 | VAR2).setName('Var')
parser.addElement(Var)

ExpressionList = Forward().setName('ExpressionList')
parser.addElement(ExpressionList)


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
BuiltInCall = Group(Aggregate | \
                STR + LPAR + Expression('expression') + RPAR    | \
                LANG + LPAR + Expression('expression') + RPAR    | \
                LANGMATCHES + LPAR + Expression('language-tag') + COMMA + Expression('language-range') + RPAR    | \
                DATATYPE + LPAR + Expression('expression') + RPAR    | \
                BOUND + LPAR + Var('var') + RPAR    | \
                IRI + LPAR + Expression('expression') + RPAR    | \
                URI + LPAR + Expression('expression') + RPAR    | \
                BNODE + (LPAR + Expression('expression') + RPAR | NIL)    | \
                RAND + NIL    | \
                ABS + LPAR + Expression('expression') + RPAR    | \
                CEIL + LPAR + Expression('expression') + RPAR    | \
                FLOOR + LPAR + Expression('expression') + RPAR    | \
                ROUND + LPAR + Expression('expression') + RPAR    | \
                CONCAT + ExpressionList('expressionList')    | \
                SubstringExpression   | \
                STRLEN + LPAR + Expression('expression') + RPAR    | \
                StrReplaceExpression  | \
                UCASE + LPAR + Expression('expression') + RPAR    | \
                LCASE + LPAR + Expression('expression') + RPAR    | \
                ENCODE_FOR_URI + LPAR + Expression('expression') + RPAR    | \
                CONTAINS + LPAR + Expression('arg1') + COMMA + Expression('arg2') + RPAR    | \
                STRSTARTS + LPAR + Expression('arg1') + COMMA + Expression('arg2') + RPAR    | \
                STRENDS + LPAR + Expression('arg1') + COMMA + Expression('arg2') + RPAR    | \
                STRBEFORE + LPAR + Expression('arg1') + COMMA + Expression('arg2') + RPAR    | \
                STRAFTER + LPAR + Expression('arg1') + COMMA + Expression('arg2') + RPAR    | \
                YEAR + LPAR + Expression('expression') + RPAR    | \
                MONTH + LPAR + Expression('expression') + RPAR    | \
                DAY + LPAR + Expression('expression') + RPAR    | \
                HOURS + LPAR + Expression('expression') + RPAR    | \
                MINUTES + LPAR + Expression('expression') + RPAR    | \
                SECONDS + LPAR + Expression('expression') + RPAR    | \
                TIMEZONE + LPAR + Expression('expression') + RPAR    | \
                TZ + LPAR + Expression('expression') + RPAR    | \
                NOW + NIL    | \
                UUID + NIL    | \
                STRUUID + NIL    | \
                MD5 + LPAR + Expression('expression') + RPAR    | \
                SHA1 + LPAR + Expression('expression') + RPAR    | \
                SHA256 + LPAR + Expression('expression') + RPAR    | \
                SHA384 + LPAR + Expression('expression') + RPAR    | \
                SHA512 + LPAR + Expression('expression') + RPAR    | \
                COALESCE + ExpressionList('expressionList')    | \
                IF + LPAR + Expression('expression1') + COMMA + Expression('expression2') + COMMA + Expression('expression3') + RPAR    | \
                STRLANG + LPAR + Expression('lexicalForm') + COMMA + Expression('langTag') + RPAR    | \
                STRDT + LPAR + Expression('lexicalForm') + COMMA + Expression('datatypeIRI') + RPAR    | \
                sameTerm + LPAR + Expression('term1') + COMMA + Expression('term2') + RPAR    | \
                isIRI + LPAR + Expression('expression') + RPAR    | \
                isURI + LPAR + Expression('expression') + RPAR    | \
                isBLANK + LPAR + Expression('expression') + RPAR    | \
                isLITERAL + LPAR + Expression('expression') + RPAR    | \
                isNUMERIC + LPAR + Expression('expression') + RPAR    | \
                RegexExpression | \
                ExistsFunc | \
                NotExistsFunc ).setName('BuiltInCall')
parser.addElement(BuiltInCall)

# [120]   BrackettedExpression      ::=   '(' Expression ')' 
BracketedExpression = Group(LPAR + Expression('expression') + RPAR).setName('BracketedExpression')
parser.addElement(BracketedExpression)

# [119]   PrimaryExpression         ::=   BrackettedExpression | BuiltInCall | iriOrFunction | RDFLiteral | NumericLiteral | BooleanLiteral | Var 
PrimaryExpression = Group(BracketedExpression | BuiltInCall | iriOrFunction('iriOrFunction') | RDFLiteral | NumericLiteral | BooleanLiteral | Var).setName('PrimaryExpression')
parser.addElement(PrimaryExpression)

# [118]   UnaryExpression   ::=     '!' PrimaryExpression 
#             | '+' PrimaryExpression 
#             | '-' PrimaryExpression 
#             | PrimaryExpression 
UnaryExpression = Group(NEGATE + PrimaryExpression | PLUS + PrimaryExpression | MINUS + PrimaryExpression | PrimaryExpression).setName('UnaryExpression')
parser.addElement(UnaryExpression)

# [117]   MultiplicativeExpression          ::=   UnaryExpression ( '*' UnaryExpression | '/' UnaryExpression )* 
MultiplicativeExpression = Group(UnaryExpression + ZeroOrMore( TIMES + UnaryExpression | DIV + UnaryExpression )).setName('MultiplicativeExpression')
parser.addElement(MultiplicativeExpression)

# [116]   AdditiveExpression        ::=   MultiplicativeExpression ( '+' MultiplicativeExpression | '-' MultiplicativeExpression | ( NumericLiteralPositive | NumericLiteralNegative ) ( ( '*' UnaryExpression ) | ( '/' UnaryExpression ) )* )* 
AdditiveExpression = Group(MultiplicativeExpression + ZeroOrMore (PLUS + MultiplicativeExpression | MINUS  + MultiplicativeExpression | (NumericLiteralPositive | NumericLiteralNegative) + ZeroOrMore (TIMES + UnaryExpression | DIV + UnaryExpression))).setName('AdditiveExpression')
parser.addElement(AdditiveExpression)

# [115]   NumericExpression         ::=   AdditiveExpression 
NumericExpression = Group(AdditiveExpression + Empty()).setName('NumericExpression')
parser.addElement(NumericExpression)

# [114]   RelationalExpression      ::=   NumericExpression ( '=' NumericExpression | '!=' NumericExpression | '<' NumericExpression | '>' NumericExpression | '<=' NumericExpression | '>=' NumericExpression | 'IN' ExpressionList | 'NOT' 'IN' ExpressionList )? 
RelationalExpression = Group(NumericExpression + Optional( EQ + NumericExpression | \
                                                         NE + NumericExpression | \
                                                         LT + NumericExpression | \
                                                         GT + NumericExpression | \
                                                         LE + NumericExpression | \
                                                         GE + NumericExpression | \
                                                         IN + ExpressionList | \
                                                         NOT_IN + ExpressionList) ).setName('RelationalExpression')
parser.addElement(RelationalExpression)

# [113]   ValueLogical      ::=   RelationalExpression 
ValueLogical = Group(RelationalExpression + Empty()).setName('ValueLogical')
parser.addElement(ValueLogical)

# [112]   ConditionalAndExpression          ::=   ValueLogical ( '&&' ValueLogical )* 
ConditionalAndExpression = Group(ValueLogical + ZeroOrMore(AND + ValueLogical)).setName('ConditionalAndExpression')
parser.addElement(ConditionalAndExpression)

# [111]   ConditionalOrExpression   ::=   ConditionalAndExpression ( '||' ConditionalAndExpression )* 
ConditionalOrExpression = Group(ConditionalAndExpression + ZeroOrMore(OR + ConditionalAndExpression)).setName('ConditionalOrExpression')
parser.addElement(ConditionalOrExpression)

# [110]   Expression        ::=   ConditionalOrExpression 
Expression << Group(ConditionalOrExpression + Empty())

# [109]   GraphTerm         ::=   iri | RDFLiteral | NumericLiteral | BooleanLiteral | BlankNode | NIL 
GraphTerm =   Group(iri | \
                RDFLiteral | \
                NumericLiteral | \
                BooleanLiteral | \
                BlankNode | \
                NIL ).setName('GraphTerm')
parser.addElement(GraphTerm)
                
# [107]   VarOrIri          ::=   Var | iri 
VarOrIri = Group(Var | iri).setName('VarOrIri')
parser.addElement(VarOrIri)

# [106]   VarOrTerm         ::=   Var | GraphTerm 
VarOrTerm = Group(Var | GraphTerm).setName('VarOrTerm')
parser.addElement(VarOrTerm)

TriplesNodePath = Forward().setName('TriplesNodePath')
parser.addElement(TriplesNodePath)

# [105]   GraphNodePath     ::=   VarOrTerm | TriplesNodePath 
GraphNodePath = Group(VarOrTerm | TriplesNodePath ).setName('GraphNodePath')
parser.addElement(GraphNodePath)

TriplesNode = Forward().setName('TriplesNode')
parser.addElement(TriplesNode)

# [104]   GraphNode         ::=   VarOrTerm | TriplesNode 
GraphNode = Group(VarOrTerm | TriplesNode).setName('GraphNode')
parser.addElement(GraphNode)

# [103]   CollectionPath    ::=   '(' GraphNodePath+ ')' 
CollectionPath = Group(LPAR + OneOrMore(GraphNodePath) + RPAR).setName('CollectionPath')
parser.addElement(CollectionPath)

# [102]   Collection        ::=   '(' GraphNode+ ')' 
Collection = Group(LPAR + OneOrMore(GraphNode) + RPAR).setName('Collection')
parser.addElement(Collection)

PropertyListPathNotEmpty = Forward().setName('PropertyListPathNotEmpty')
parser.addElement(PropertyListPathNotEmpty)

# [101]   BlankNodePropertyListPath         ::=   '[' PropertyListPathNotEmpty ']'
BlankNodePropertyListPath = Group(LBRACK + PropertyListPathNotEmpty + RBRACK ).setName('BlankNodePropertyListPath')
parser.addElement(BlankNodePropertyListPath)

# [100]   TriplesNodePath   ::=   CollectionPath | BlankNodePropertyListPath 
TriplesNodePath << Group(CollectionPath | BlankNodePropertyListPath)

PropertyListNotEmpty = Forward().setName('PropertyListNotEmpty')
parser.addElement(PropertyListNotEmpty)

# [99]    BlankNodePropertyList     ::=   '[' PropertyListNotEmpty ']' 
BlankNodePropertyList = Group(LBRACK + PropertyListNotEmpty + RBRACK ).setName('BlankNodePropertyList')
parser.addElement(BlankNodePropertyList)

# [98]    TriplesNode       ::=   Collection | BlankNodePropertyList 
TriplesNode << Group(Collection | BlankNodePropertyList)

# [97]    Integer   ::=   INTEGER 
Integer = Group(INTEGER + Empty()).setName('Integer')
parser.addElement(Integer)

# [96]    PathOneInPropertySet      ::=   iri | 'a' | '^' ( iri | 'a' ) 
PathOneInPropertySet = Group(iri | TYPE | (INVERSE  + ( iri | TYPE ))).setName('PathOneInPropertySet')
parser.addElement(PathOneInPropertySet)

# [95]    PathNegatedPropertySet    ::=   PathOneInPropertySet | '(' ( PathOneInPropertySet ( '|' PathOneInPropertySet )* )? ')' 
PathNegatedPropertySet = Group(PathOneInPropertySet | (LPAR + Group(Optional(separatedList(PathOneInPropertySet, sep='|'))('pathinonepropertyset')) + RPAR)).setName('PathNegatedPropertySet')
parser.addElement(PathNegatedPropertySet)

Path = Forward().setName('Path')
parser.addElement(Path)

# [94]    PathPrimary       ::=   iri | 'a' | '!' PathNegatedPropertySet | '(' Path ')' 
PathPrimary = Group(iri | TYPE | (NEGATE + PathNegatedPropertySet) | (LPAR + Path + RPAR)).setName('PathPrimary')
parser.addElement(PathPrimary)

# [93]    PathMod   ::=   '?' | '*' | '+' 
PathMod = Group((~VAR1 + Literal('?')) | Literal('*') | Literal('+')).setName('PathMod')
parser.addElement(PathMod)

# [91]    PathElt   ::=   PathPrimary PathMod? 
PathElt = Group(PathPrimary + Optional(PathMod) ).setName('PathElt')
parser.addElement(PathElt)

# [92]    PathEltOrInverse          ::=   PathElt | '^' PathElt 
PathEltOrInverse = Group(PathElt | (INVERSE + PathElt)).setName('PathEltOrInverse')
parser.addElement(PathEltOrInverse)

# [90]    PathSequence      ::=   PathEltOrInverse ( '/' PathEltOrInverse )* 
PathSequence = Group(separatedList(PathEltOrInverse, sep='/')).setName('PathSequence')
parser.addElement(PathSequence)

# [89]    PathAlternative   ::=   PathSequence ( '|' PathSequence )* 
PathAlternative = Group(separatedList(PathSequence, sep='|')).setName('PathAlternative')
parser.addElement(PathAlternative)
 
# [88]    Path      ::=   PathAlternative
Path << Group(PathAlternative + Empty())

# [87]    ObjectPath        ::=   GraphNodePath 
ObjectPath = Group(GraphNodePath + Empty() ).setName('ObjectPath')
parser.addElement(ObjectPath)

# [86]    ObjectListPath    ::=   ObjectPath ( ',' ObjectPath )* 
ObjectListPath = Group(separatedList(ObjectPath)).setName('ObjectListPath')
parser.addElement(ObjectListPath)

# [85]    VerbSimple        ::=   Var 
VerbSimple = Group(Var + Empty() ).setName('VerbSimple')
parser.addElement(VerbSimple)

# [84]    VerbPath          ::=   Path
VerbPath = Group(Path + Empty() ).setName('VerbPath')
parser.addElement(VerbPath)

# [80]    Object    ::=   GraphNode 
Object = Group(GraphNode + Empty() ).setName('Object')
parser.addElement(Object)
 
# [79]    ObjectList        ::=   Object ( ',' Object )* 
ObjectList = Group(separatedList(Object)).setName('ObjectList')
parser.addElement(ObjectList)

# [83]    PropertyListPathNotEmpty          ::=   ( VerbPath | VerbSimple ) ObjectListPath ( ';' ( ( VerbPath | VerbSimple ) ObjectList )? )* 
PropertyListPathNotEmpty << Group((VerbPath | VerbSimple) + ObjectListPath +  ZeroOrMore(SEMICOL + Optional(( VerbPath | VerbSimple) + ObjectList)))

# [82]    PropertyListPath          ::=   PropertyListPathNotEmpty? 
PropertyListPath = Group(Optional(PropertyListPathNotEmpty)).setName('PropertyListPath')
parser.addElement(PropertyListPath)

# [81]    TriplesSameSubjectPath    ::=   VarOrTerm PropertyListPathNotEmpty | TriplesNodePath PropertyListPath 
TriplesSameSubjectPath = Group((VarOrTerm + PropertyListPathNotEmpty) | (TriplesNodePath + PropertyListPath)).setName('TriplesSameSubjectPath')
parser.addElement(TriplesSameSubjectPath)

# [78]    Verb      ::=   VarOrIri | 'a' 
Verb = Group(VarOrIri | TYPE).setName('Verb')
parser.addElement(Verb)

# [77]    PropertyListNotEmpty      ::=   Verb ObjectList ( ';' ( Verb ObjectList )? )* 
PropertyListNotEmpty << Group(Verb + ObjectList + ZeroOrMore(SEMICOL + Optional(Verb + ObjectList)))

# [76]    PropertyList      ::=   PropertyListNotEmpty?
PropertyList = Group(Optional(PropertyListNotEmpty) ).setName('PropertyList')
parser.addElement(PropertyList)

# [75]    TriplesSameSubject        ::=   VarOrTerm PropertyListNotEmpty | TriplesNode PropertyList
TriplesSameSubject = Group((VarOrTerm + PropertyListNotEmpty) | (TriplesNode + PropertyList) ).setName('TriplesSameSubject')
parser.addElement(TriplesSameSubject)

# [74]    ConstructTriples          ::=   TriplesSameSubject ( '.' ConstructTriples? )? 
ConstructTriples = Group(separatedList(TriplesSameSubject, sep='.') + Optional(PERIOD)).setName('ConstructTriples')
parser.addElement(ConstructTriples)

# [73]    ConstructTemplate         ::=   '{' ConstructTriples? '}'
ConstructTemplate = Group(LCURL + Optional(ConstructTriples) + RCURL ).setName('ConstructTemplate')
parser.addElement(ConstructTemplate)

# [72]    ExpressionList    ::=   NIL | '(' Expression ( ',' Expression )* ')' 
ExpressionList << Group(NIL | (LPAR + separatedList(Expression) + RPAR))

# [70]    FunctionCall      ::=   iri ArgList 
FunctionCall = Group(iri + ArgList).setName('FunctionCall')
parser.addElement(FunctionCall)

# [69]    Constraint        ::=   BrackettedExpression | BuiltInCall | FunctionCall 
Constraint = Group(BracketedExpression | BuiltInCall | FunctionCall).setName('Constraint')
parser.addElement(Constraint)

# [68]    Filter    ::=   'FILTER' Constraint
Filter = Group(FILTER + Constraint('constraint')).setName('Filter')
parser.addElement(Filter)

# [67]    GroupOrUnionGraphPattern          ::=   GroupGraphPattern ( 'UNION' GroupGraphPattern )* 
GroupOrUnionGraphPattern = Group(GroupGraphPattern + ZeroOrMore(UNION + GroupGraphPattern) ).setName('GroupOrUnionGraphPattern')
parser.addElement(GroupOrUnionGraphPattern)

# [66]    MinusGraphPattern         ::=   'MINUS' GroupGraphPattern
MinusGraphPattern = Group(SUBTRACT + GroupGraphPattern ).setName('MinusGraphPattern')
parser.addElement(MinusGraphPattern)

# [65]    DataBlockValue    ::=   iri | RDFLiteral | NumericLiteral | BooleanLiteral | 'UNDEF' 
DataBlockValue = Group(iri | RDFLiteral | NumericLiteral | BooleanLiteral | UNDEF).setName('DataBlockValue')
parser.addElement(DataBlockValue)

# [64]    InlineDataFull    ::=   ( NIL | '(' Var* ')' ) '{' ( '(' DataBlockValue* ')' | NIL )* '}' 
InlineDataFull = Group(( NIL | (LPAR + ZeroOrMore(Var) + RPAR)) + LCURL +  ZeroOrMore((LPAR + ZeroOrMore(DataBlockValue) + RPAR) | NIL) + RCURL ).setName('InlineDataFull')
parser.addElement(InlineDataFull)

# [63]    InlineDataOneVar          ::=   Var '{' DataBlockValue* '}' 
InlineDataOneVar = Group(Var + LCURL + ZeroOrMore(DataBlockValue) + RCURL ).setName('InlineDataOneVar')
parser.addElement(InlineDataOneVar)

# [62]    DataBlock         ::=   InlineDataOneVar | InlineDataFull 
DataBlock = Group(InlineDataOneVar | InlineDataFull).setName('DataBlock')
parser.addElement(DataBlock)

# [61]    InlineData        ::=   'VALUES' DataBlock 
InlineData = Group(VALUES + DataBlock ).setName('InlineData')
parser.addElement(InlineData)

# [60]    Bind      ::=   'BIND' '(' Expression 'AS' Var ')' 
Bind = Group(BIND + LPAR + Expression + AS + Var + RPAR ).setName('Bind')
parser.addElement(Bind)

# [59]    ServiceGraphPattern       ::=   'SERVICE' 'SILENT'? VarOrIri GroupGraphPattern 
ServiceGraphPattern = Group(SERVICE + Optional(SILENT) + VarOrIri + GroupGraphPattern ).setName('ServiceGraphPattern')
parser.addElement(ServiceGraphPattern)

# [58]    GraphGraphPattern         ::=   'GRAPH' VarOrIri GroupGraphPattern 
GraphGraphPattern = Group(GRAPH + VarOrIri + GroupGraphPattern ).setName('GraphGraphPattern')
parser.addElement(GraphGraphPattern)

# [57]    OptionalGraphPattern      ::=   'OPTIONAL' GroupGraphPattern 
OptionalGraphPattern = Group(OPTIONAL + GroupGraphPattern ).setName('OptionalGraphPattern')
parser.addElement(OptionalGraphPattern)

# [56]    GraphPatternNotTriples    ::=   GroupOrUnionGraphPattern | OptionalGraphPattern | MinusGraphPattern | GraphGraphPattern | ServiceGraphPattern | Filter | Bind | InlineData 
GraphPatternNotTriples = Group(GroupOrUnionGraphPattern | OptionalGraphPattern | MinusGraphPattern | GraphGraphPattern | ServiceGraphPattern | Filter | Bind | InlineData ).setName('GraphPatternNotTriples')
parser.addElement(GraphPatternNotTriples)
                                           
# [55]    TriplesBlock      ::=   TriplesSameSubjectPath ( '.' TriplesBlock? )? 
TriplesBlock = Group(separatedList(TriplesSameSubjectPath, sep='.')('subjpath') + Optional(PERIOD)).setName('TriplesBlock')
parser.addElement(TriplesBlock)

# [54]    GroupGraphPatternSub      ::=   TriplesBlock? ( GraphPatternNotTriples '.'? TriplesBlock? )* 
GroupGraphPatternSub = Group(Optional(TriplesBlock) + ZeroOrMore(GraphPatternNotTriples + Optional(PERIOD) + Optional(TriplesBlock)) ).setName('GroupGraphPatternSub')
parser.addElement(GroupGraphPatternSub)

SubSelect = Forward().setName('SubSelect')
parser.addElement(SubSelect)

# [53]    GroupGraphPattern         ::=   '{' ( SubSelect | GroupGraphPatternSub ) '}' 
GroupGraphPattern << Group(LCURL + (SubSelect | GroupGraphPatternSub)('pattern') + RCURL)

# [52]    TriplesTemplate   ::=   TriplesSameSubject ( '.' TriplesTemplate? )? 
TriplesTemplate = Group(separatedList(TriplesSameSubject, sep='.') + Optional(PERIOD)).setName('TriplesTemplate')
parser.addElement(TriplesTemplate)

# [51]    QuadsNotTriples   ::=   'GRAPH' VarOrIri '{' TriplesTemplate? '}' 
QuadsNotTriples = Group(GRAPH + VarOrIri + LCURL + Optional(TriplesTemplate) + RCURL ).setName('QuadsNotTriples')
parser.addElement(QuadsNotTriples)

# [50]    Quads     ::=   TriplesTemplate? ( QuadsNotTriples '.'? TriplesTemplate? )* 
Quads = Group(Optional(TriplesTemplate) + ZeroOrMore(QuadsNotTriples + Optional(PERIOD) + Optional(TriplesTemplate)) ).setName('Quads')
parser.addElement(Quads)

# [49]    QuadData          ::=   '{' Quads '}' 
QuadData = Group(LCURL + Quads + RCURL ).setName('QuadData')
parser.addElement(QuadData)

# [48]    QuadPattern       ::=   '{' Quads '}' 
QuadPattern = Group(LCURL + Quads + RCURL ).setName('QuadPattern')
parser.addElement(QuadPattern)

# [46]    GraphRef          ::=   'GRAPH' iri 
GraphRef = Group(GRAPH + iri ).setName('GraphRef')
parser.addElement(GraphRef)

# [47]    GraphRefAll       ::=   GraphRef | 'DEFAULT' | 'NAMED' | 'ALL' 
GraphRefAll = Group(GraphRef | DEFAULT | NAMED | ALL ).setName('GraphRefAll')
parser.addElement(GraphRefAll)

# [45]    GraphOrDefault    ::=   'DEFAULT' | 'GRAPH'? iri 
GraphOrDefault = Group(DEFAULT | (Optional(GRAPH) + iri) ).setName('GraphOrDefault')
parser.addElement(GraphOrDefault)

# [44]    UsingClause       ::=   'USING' ( iri | 'NAMED' iri ) 
UsingClause = Group(USING + (iri | (NAMED + iri)) ).setName('UsingClause')
parser.addElement(UsingClause)

# [43]    InsertClause      ::=   'INSERT' QuadPattern 
InsertClause = Group(INSERT + QuadPattern ).setName('InsertClause')
parser.addElement(InsertClause)

# [42]    DeleteClause      ::=   'DELETE' QuadPattern 
DeleteClause = Group(DELETE + QuadPattern ).setName('DeleteClause')
parser.addElement(DeleteClause)

# [41]    Modify    ::=   ( 'WITH' iri )? ( DeleteClause InsertClause? | InsertClause ) UsingClause* 'WHERE' GroupGraphPattern 
Modify = Group(Optional(WITH + iri) + ( (DeleteClause + Optional(InsertClause) ) | InsertClause ) + ZeroOrMore(UsingClause) + WHERE + GroupGraphPattern ).setName('Modify')
parser.addElement(Modify)

# [40]    DeleteWhere       ::=   'DELETE WHERE' QuadPattern 
DeleteWhere = Group(DELETE_WHERE + QuadPattern ).setName('DeleteWhere')
parser.addElement(DeleteWhere)

# [39]    DeleteData        ::=   'DELETE DATA' QuadData 
DeleteData = Group(DELETE_DATA + QuadData ).setName('DeleteData')
parser.addElement(DeleteData)

# [38]    InsertData        ::=   'INSERT DATA' QuadData 
InsertData = Group(INSERT_DATA + QuadData ).setName('InsertData')
parser.addElement(InsertData)

# [37]    Copy      ::=   'COPY' 'SILENT'? GraphOrDefault 'TO' GraphOrDefault 
Copy = Group(COPY + Optional(SILENT) + GraphOrDefault + TO + GraphOrDefault ).setName('Copy')
parser.addElement(Copy)

# [36]    Move      ::=   'MOVE' 'SILENT'? GraphOrDefault 'TO' GraphOrDefault 
Move = Group(MOVE + Optional(SILENT) + GraphOrDefault + TO + GraphOrDefault ).setName('Move')
parser.addElement(Move)

# [35]    Add       ::=   'ADD' 'SILENT'? GraphOrDefault 'TO' GraphOrDefault 
Add = Group(ADD + Optional(SILENT) + GraphOrDefault + TO + GraphOrDefault ).setName('Add')
parser.addElement(Add)

# [34]    Create    ::=   'CREATE' 'SILENT'? GraphRef 
Create = Group(CREATE + Optional(SILENT) + GraphRef).setName('Create')
parser.addElement(Create)

# [33]    Drop      ::=   'DROP' 'SILENT'? GraphRefAll 
Drop = Group(DROP + Optional(SILENT) + GraphRefAll).setName('Drop')
parser.addElement(Drop)

# [32]    Clear     ::=   'CLEAR' 'SILENT'? GraphRefAll 
Clear = Group(CLEAR + Optional(SILENT) + GraphRefAll ).setName('Clear')
parser.addElement(Clear)

# [31]    Load      ::=   'LOAD' 'SILENT'? iri ( 'INTO' GraphRef )? 
Load = Group(LOAD + Optional(SILENT) + iri  + Optional(INTO + GraphRef)).setName('Load')
parser.addElement(Load)

# [30]    Update1   ::=   Load | Clear | Drop | Add | Move | Copy | Create | InsertData | DeleteData | DeleteWhere | Modify 
Update1 = Group(Load | Clear | Drop | Add | Move | Copy | Create | InsertData | DeleteData | DeleteWhere | Modify ).setName('Update1')
parser.addElement(Update1)

Prologue = Forward().setName('Prologue')
parser.addElement(Prologue)

Update = Forward().setName('Update')
parser.addElement(Update)

# [29]    Update    ::=   Prologue ( Update1 ( ';' Update )? )? 
Update << Group(Prologue('prologue') + Optional(Update1 + Optional(SEMICOL + Update)))

# [28]    ValuesClause      ::=   ( 'VALUES' DataBlock )? 
ValuesClause = Group(Optional(VALUES + DataBlock) ).setName('ValuesClause')
parser.addElement(ValuesClause)

# [27]    OffsetClause      ::=   'OFFSET' INTEGER 
OffsetClause = Group(OFFSET + INTEGER ).setName('OffsetClause')
parser.addElement(OffsetClause)

# [26]    LimitClause       ::=   'LIMIT' INTEGER 
LimitClause = Group(LIMIT + INTEGER ).setName('LimitClause')
parser.addElement(LimitClause)

# [25]    LimitOffsetClauses        ::=   LimitClause OffsetClause? | OffsetClause LimitClause? 
LimitOffsetClauses = Group((LimitClause + Optional(OffsetClause)) | (OffsetClause + Optional(LimitClause))).setName('LimitOffsetClauses')
parser.addElement(LimitOffsetClauses)

# [24]    OrderCondition    ::=   ( ( 'ASC' | 'DESC' ) BrackettedExpression ) | ( Constraint | Var ) 
OrderCondition =   Group(((ASC | DESC) + BracketedExpression) | (Constraint('constraint') | Var)).setName('OrderCondition')
parser.addElement(OrderCondition)

# [23]    OrderClause       ::=   'ORDER' 'BY' OrderCondition+ 
OrderClause = Group(ORDER_BY + OneOrMore(OrderCondition) ).setName('OrderClause')
parser.addElement(OrderClause)

# [22]    HavingCondition   ::=   Constraint 
HavingCondition = Group(Constraint('constraint')).setName('HavingCondition')
parser.addElement(HavingCondition)

# [21]    HavingClause      ::=   'HAVING' HavingCondition+ 
HavingClause = Group(HAVING + OneOrMore(HavingCondition) ).setName('HavingClause')
parser.addElement(HavingClause)

# [20]    GroupCondition    ::=   BuiltInCall | FunctionCall | '(' Expression ( 'AS' Var )? ')' | Var 
GroupCondition = Group(BuiltInCall | FunctionCall | (LPAR + Expression + Optional(AS + Var) + RPAR) | Var ).setName('GroupCondition')
parser.addElement(GroupCondition)

# [19]    GroupClause       ::=   'GROUP' 'BY' GroupCondition+ 
GroupClause = Group(GROUP_BY + OneOrMore(GroupCondition) ).setName('GroupClause')
parser.addElement(GroupClause)

# [18]    SolutionModifier          ::=   GroupClause? HavingClause? OrderClause? LimitOffsetClauses? 
SolutionModifier = Group(Optional(GroupClause) + Optional(HavingClause) + Optional(OrderClause) + Optional(LimitOffsetClauses) ).setName('SolutionModifier')
parser.addElement(SolutionModifier)

# [17]    WhereClause       ::=   'WHERE'? GroupGraphPattern 
WhereClause = Group(Optional(WHERE) + GroupGraphPattern ).setName('WhereClause')
parser.addElement(WhereClause)

# [16]    SourceSelector    ::=   iri 
SourceSelector = Group(iri).setName('SourceSelector')
parser.addElement(SourceSelector)

# [15]    NamedGraphClause          ::=   'NAMED' SourceSelector 
NamedGraphClause = Group(NAMED + SourceSelector ).setName('NamedGraphClause')
parser.addElement(NamedGraphClause)

# [14]    DefaultGraphClause        ::=   SourceSelector 
DefaultGraphClause = Group(SourceSelector).setName('DefaultGraphClause')
parser.addElement(DefaultGraphClause)

# [13]    DatasetClause     ::=   'FROM' ( DefaultGraphClause | NamedGraphClause ) 
DatasetClause = Group(FROM + (DefaultGraphClause | NamedGraphClause) ).setName('DatasetClause')
parser.addElement(DatasetClause)

# [12]    AskQuery          ::=   'ASK' DatasetClause* WhereClause SolutionModifier 
AskQuery = Group(ASK + ZeroOrMore(DatasetClause) + WhereClause('where') + SolutionModifier ).setName('AskQuery')
parser.addElement(AskQuery)

# [11]    DescribeQuery     ::=   'DESCRIBE' ( VarOrIri+ | '*' ) DatasetClause* WhereClause? SolutionModifier 
DescribeQuery = Group(DESCRIBE + (OneOrMore(VarOrIri) | ALL_VALUES) + ZeroOrMore(DatasetClause) + Optional(WhereClause('where')) + SolutionModifier ).setName('DescribeQuery')
parser.addElement(DescribeQuery)

# [10]    ConstructQuery    ::=   'CONSTRUCT' ( ConstructTemplate DatasetClause* WhereClause SolutionModifier | DatasetClause* 'WHERE' '{' TriplesTemplate? '}' SolutionModifier ) 
ConstructQuery = Group(CONSTRUCT + ((ConstructTemplate + ZeroOrMore(DatasetClause) + WhereClause('where') + SolutionModifier) | \
                                      (ZeroOrMore(DatasetClause) + WHERE + LCURL +  Optional(TriplesTemplate) + RCURL + SolutionModifier))).setName('ConstructQuery')
parser.addElement(ConstructQuery)

# [9]     SelectClause      ::=   'SELECT' ( 'DISTINCT' | 'REDUCED' )? ( ( Var | ( '(' Expression 'AS' Var ')' ) )+ | '*' ) 
SelectClause = Group(SELECT + Optional(DISTINCT | REDUCED) + ( OneOrMore(Var | (LPAR + Expression + AS + Var + RPAR)) | ALL_VALUES ) ).setName('SelectClause')
parser.addElement(SelectClause)

# [8]     SubSelect         ::=   SelectClause WhereClause SolutionModifier ValuesClause 
SubSelect << Group(SelectClause + WhereClause('where') + SolutionModifier + ValuesClause)

# [7]     SelectQuery       ::=   SelectClause DatasetClause* WhereClause SolutionModifier 
SelectQuery = Group(SelectClause + ZeroOrMore(DatasetClause) + WhereClause('where') + SolutionModifier ).setName('SelectQuery')
parser.addElement(SelectQuery)

# [6]     PrefixDecl        ::=   'PREFIX' PNAME_NS IRIREF 
PrefixDecl = Group(PREFIX('prefix') + PNAME_NS + IRIREF ).setName('PrefixDecl')
parser.addElement(PrefixDecl)

# [5]     BaseDecl          ::=   'BASE' IRIREF 
BaseDecl = Group(BASE + IRIREF ).setName('BaseDecl')
parser.addElement(BaseDecl)

# [4]     Prologue          ::=   ( BaseDecl | PrefixDecl )* 
Prologue << Group(ZeroOrMore(BaseDecl('base') | PrefixDecl('prefix')))

# [3]     UpdateUnit        ::=   Update 
UpdateUnit = Group(Update('update')).setName('UpdateUnit')
parser.addElement(UpdateUnit)

# [2]     Query     ::=   Prologue ( SelectQuery | ConstructQuery | DescribeQuery | AskQuery ) ValuesClause 
Query = Group(Prologue('prologue') + ( SelectQuery | ConstructQuery | DescribeQuery | AskQuery ) + ValuesClause ).setName('Query')
parser.addElement(Query)

# [1]     QueryUnit         ::=   Query 
QueryUnit = Group(Query).setName('QueryUnit')
parser.addElement(QueryUnit)
 


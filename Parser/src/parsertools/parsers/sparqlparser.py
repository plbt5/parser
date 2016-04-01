'''
Created on 28 mrt. 2016

@author: jeroenbruijning
'''
from pyparsing import *
from parsertools.extras import separatedList
from parsertools.base import ParseInfo, parseInfoFunc, Parser
from parsertools import SparqlParserException

    
# def parsertools.addElement(pattern):
#     setattr(parsertools, pattern.name, type(pattern.name, (ParseInfo,), {'pattern': pattern}))
#     pattern.setParseAction(parseInfoFunc(getattr(parsertools, pattern.name)))
    
sparqlparser = Parser()

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
    stripped = stripComments(querystring)
    # TODO: finish
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
    '''Entry point to parse any SPARQL query'''
    s = prepareQuery(querystring)
    try:
        result = sparqlparser.QueryUnit(s)
    except ParseException:
        try:
            result = sparqlparser.UpdateUnit(s)
        except ParseException:
            raise SparqlParserException('Query {} cannot be parsed'.format(querystring))
    assert checkQueryResult(result), 'Fault in postprocessing query {}'.format(querystring)
    return result
# Patterns
#

#
# Brackets and interpunction
#


LPAR_p = Literal('(').setName('LPAR')
sparqlparser.addElement(LPAR_p)

RPAR_p = Literal(')').setName('RPAR')
sparqlparser.addElement(RPAR_p)

LBRACK_p = Literal('[').setName('LBRACK')
sparqlparser.addElement(LBRACK_p)

RBRACK_p = Literal(']').setName('RBRACK')
sparqlparser.addElement(RBRACK_p)

LCURL_p = Literal('{').setName('LCURL')
sparqlparser.addElement(LCURL_p)

RCURL_p = Literal('}').setName('RCURL')
sparqlparser.addElement(RCURL_p)

SEMICOL_p = Literal(';').setName('SEMICOL')
sparqlparser.addElement(SEMICOL_p)

PERIOD_p = Literal('.').setName('PERIOD')
sparqlparser.addElement(PERIOD_p)

COMMA_p = Literal(',').setName('COMMA')
sparqlparser.addElement(COMMA_p)

#
# Operators
#

NEGATE_p = Literal('!').setName('NEGATE')
sparqlparser.addElement(NEGATE_p)

PLUS_p = Literal('+').setName('PLUS')
sparqlparser.addElement(PLUS_p)

MINUS_p = Literal('-').setName('MINUS')
sparqlparser.addElement(MINUS_p)

TIMES_p = Literal('*').setName('TIMES')
sparqlparser.addElement(TIMES_p)

DIV_p = Literal('/').setName('DIV')
sparqlparser.addElement(DIV_p)

EQ_p = Literal('=').setName('EQ')
sparqlparser.addElement(EQ_p)

NE_p = Literal('!=').setName('NE')
sparqlparser.addElement(NE_p)

GT_p = Literal('>').setName('GT')
sparqlparser.addElement(GT_p)

LT_p = Literal('<').setName('LT')
sparqlparser.addElement(LT_p)

GE_p = Literal('>=').setName('GE')
sparqlparser.addElement(GE_p)

LE_p = Literal('<=').setName('LE')
sparqlparser.addElement(LE_p)

AND_p = Literal('&&').setName('AND')
sparqlparser.addElement(AND_p)

OR_p = Literal('||').setName('OR')
sparqlparser.addElement(OR_p)

INVERSE_p = Literal('^').setName('INVERSE')
sparqlparser.addElement(INVERSE_p)

#
# Keywords
#

ALL_VALUES_p = Literal('*').setName('ALL_VALUES')
sparqlparser.addElement(ALL_VALUES_p)

TYPE_p = Keyword('a').setName('TYPE')
sparqlparser.addElement(TYPE_p)

DISTINCT_p = CaselessKeyword('DISTINCT').setName('DISTINCT')
sparqlparser.addElement(DISTINCT_p)

COUNT_p = CaselessKeyword('COUNT').setName('COUNT')
sparqlparser.addElement(COUNT_p)

SUM_p = CaselessKeyword('SUM').setName('SUM')
sparqlparser.addElement(SUM_p)

MIN_p = CaselessKeyword('MIN').setName('MIN')
sparqlparser.addElement(MIN_p)

MAX_p = CaselessKeyword('MAX').setName('MAX')
sparqlparser.addElement(MAX_p)

AVG_p = CaselessKeyword('AVG').setName('AVG')
sparqlparser.addElement(AVG_p)

SAMPLE_p = CaselessKeyword('SAMPLE').setName('SAMPLE')
sparqlparser.addElement(SAMPLE_p)

GROUP_CONCAT_p = CaselessKeyword('GROUP_CONCAT').setName('GROUP_CONCAT')
sparqlparser.addElement(GROUP_CONCAT_p)

SEPARATOR_p = CaselessKeyword('SEPARATOR').setName('SEPARATOR')
sparqlparser.addElement(SEPARATOR_p)

NOT_p = (CaselessKeyword('NOT') + NotAny(CaselessKeyword('EXISTS') | CaselessKeyword('IN'))).setName('NOT')
sparqlparser.addElement(NOT_p)

EXISTS_p = CaselessKeyword('EXISTS').setName('EXISTS')
sparqlparser.addElement(EXISTS_p)

NOT_EXISTS_p = (CaselessKeyword('NOT') + CaselessKeyword('EXISTS')).setName('NOT_EXISTS')
sparqlparser.addElement(NOT_EXISTS_p)

REPLACE_p = CaselessKeyword('REPLACE').setName('REPLACE')
sparqlparser.addElement(REPLACE_p)

SUBSTR_p = CaselessKeyword('SUBSTR').setName('SUBSTR')
sparqlparser.addElement(SUBSTR_p)

REGEX_p = CaselessKeyword('REGEX').setName('REGEX')
sparqlparser.addElement(REGEX_p)

STR_p = CaselessKeyword('STR').setName('STR')
sparqlparser.addElement(STR_p)

LANG_p = CaselessKeyword('LANG').setName('LANG')
sparqlparser.addElement(LANG_p)

LANGMATCHES_p = CaselessKeyword('LANGMATCHES').setName('LANGMATCHES')
sparqlparser.addElement(LANGMATCHES_p)

DATATYPE_p = CaselessKeyword('DATATYPE').setName('DATATYPE')
sparqlparser.addElement(DATATYPE_p)

BOUND_p = CaselessKeyword('BOUND').setName('BOUND')
sparqlparser.addElement(BOUND_p)

IRI_p = CaselessKeyword('IRI').setName('IRI')
sparqlparser.addElement(IRI_p)

URI_p = CaselessKeyword('URI').setName('URI')
sparqlparser.addElement(URI_p)

BNODE_p = CaselessKeyword('BNODE').setName('BNODE')
sparqlparser.addElement(BNODE_p)

RAND_p = CaselessKeyword('RAND').setName('RAND')
sparqlparser.addElement(RAND_p)

ABS_p = CaselessKeyword('ABS').setName('ABS')
sparqlparser.addElement(ABS_p)

CEIL_p = CaselessKeyword('CEIL').setName('CEIL')
sparqlparser.addElement(CEIL_p)

FLOOR_p = CaselessKeyword('FLOOR').setName('FLOOR')
sparqlparser.addElement(FLOOR_p)

ROUND_p = CaselessKeyword('ROUND').setName('ROUND')
sparqlparser.addElement(ROUND_p)

CONCAT_p = CaselessKeyword('CONCAT').setName('CONCAT')
sparqlparser.addElement(CONCAT_p)

STRLEN_p = CaselessKeyword('STRLEN').setName('STRLEN')
sparqlparser.addElement(STRLEN_p)

UCASE_p = CaselessKeyword('UCASE').setName('UCASE')
sparqlparser.addElement(UCASE_p)

LCASE_p = CaselessKeyword('LCASE').setName('LCASE')
sparqlparser.addElement(LCASE_p)

ENCODE_FOR_URI_p = CaselessKeyword('ENCODE_FOR_URI').setName('ENCODE_FOR_URI')
sparqlparser.addElement(ENCODE_FOR_URI_p)

CONTAINS_p = CaselessKeyword('CONTAINS').setName('CONTAINS')
sparqlparser.addElement(CONTAINS_p)

STRSTARTS_p = CaselessKeyword('STRSTARTS').setName('STRSTARTS')
sparqlparser.addElement(STRSTARTS_p)

STRENDS_p = CaselessKeyword('STRENDS').setName('STRENDS')
sparqlparser.addElement(STRENDS_p)

STRBEFORE_p = CaselessKeyword('STRBEFORE').setName('STRBEFORE')
sparqlparser.addElement(STRBEFORE_p)

STRAFTER_p = CaselessKeyword('STRAFTER').setName('STRAFTER')
sparqlparser.addElement(STRAFTER_p)

YEAR_p = CaselessKeyword('YEAR').setName('YEAR')
sparqlparser.addElement(YEAR_p)

MONTH_p = CaselessKeyword('MONTH').setName('MONTH')
sparqlparser.addElement(MONTH_p)

DAY_p = CaselessKeyword('DAY').setName('DAY')
sparqlparser.addElement(DAY_p)

HOURS_p = CaselessKeyword('HOURS').setName('HOURS')
sparqlparser.addElement(HOURS_p)

MINUTES_p = CaselessKeyword('MINUTES').setName('MINUTES')
sparqlparser.addElement(MINUTES_p)

SECONDS_p = CaselessKeyword('SECONDS').setName('SECONDS')
sparqlparser.addElement(SECONDS_p)

TIMEZONE_p = CaselessKeyword('TIMEZONE').setName('TIMEZONE')
sparqlparser.addElement(TIMEZONE_p)

TZ_p = CaselessKeyword('TZ').setName('TZ')
sparqlparser.addElement(TZ_p)

NOW_p = CaselessKeyword('NOW').setName('NOW')
sparqlparser.addElement(NOW_p)

UUID_p = CaselessKeyword('UUID').setName('UUID')
sparqlparser.addElement(UUID_p)

STRUUID_p = CaselessKeyword('STRUUID').setName('STRUUID')
sparqlparser.addElement(STRUUID_p)

MD5_p = CaselessKeyword('MD5').setName('MD5')
sparqlparser.addElement(MD5_p)

SHA1_p = CaselessKeyword('SHA1').setName('SHA1')
sparqlparser.addElement(SHA1_p)

SHA256_p = CaselessKeyword('SHA256').setName('SHA256')
sparqlparser.addElement(SHA256_p)

SHA384_p = CaselessKeyword('SHA384').setName('SHA384')
sparqlparser.addElement(SHA384_p)

SHA512_p = CaselessKeyword('SHA512').setName('SHA512')
sparqlparser.addElement(SHA512_p)

COALESCE_p = CaselessKeyword('COALESCE').setName('COALESCE')
sparqlparser.addElement(COALESCE_p)

IF_p = CaselessKeyword('IF').setName('IF')
sparqlparser.addElement(IF_p)

STRLANG_p = CaselessKeyword('STRLANG').setName('STRLANG')
sparqlparser.addElement(STRLANG_p)

STRDT_p = CaselessKeyword('STRDT').setName('STRDT')
sparqlparser.addElement(STRDT_p)

sameTerm_p = CaselessKeyword('sameTerm').setName('sameTerm')
sparqlparser.addElement(sameTerm_p)

isIRI_p = CaselessKeyword('isIRI').setName('isIRI')
sparqlparser.addElement(isIRI_p)

isURI_p = CaselessKeyword('isURI').setName('isURI')
sparqlparser.addElement(isURI_p)

isBLANK_p = CaselessKeyword('isBLANK').setName('isBLANK')
sparqlparser.addElement(isBLANK_p)

isLITERAL_p = CaselessKeyword('isLITERAL').setName('isLITERAL')
sparqlparser.addElement(isLITERAL_p)

isNUMERIC_p = CaselessKeyword('isNUMERIC').setName('isNUMERIC')
sparqlparser.addElement(isNUMERIC_p)

IN_p = CaselessKeyword('IN').setName('IN')
sparqlparser.addElement(IN_p)

NOT_IN_p = (CaselessKeyword('NOT') + CaselessKeyword('IN')).setName('NOT_IN')
sparqlparser.addElement(NOT_IN_p)

FILTER_p = CaselessKeyword('FILTER').setName('FILTER')
sparqlparser.addElement(FILTER_p)

UNION_p = CaselessKeyword('UNION').setName('UNION')
sparqlparser.addElement(UNION_p)

SUBTRACT_p = CaselessKeyword('MINUS').setName('SUBTRACT')
sparqlparser.addElement(SUBTRACT_p)

UNDEF_p = CaselessKeyword('UNDEF').setName('UNDEF')
sparqlparser.addElement(UNDEF_p)

VALUES_p = CaselessKeyword('VALUES').setName('VALUES')
sparqlparser.addElement(VALUES_p)

BIND_p = CaselessKeyword('BIND').setName('BIND')
sparqlparser.addElement(BIND_p)

AS_p = CaselessKeyword('AS').setName('AS')
sparqlparser.addElement(AS_p)

SERVICE_p = CaselessKeyword('SERVICE').setName('SERVICE')
sparqlparser.addElement(SERVICE_p)

SILENT_p = CaselessKeyword('SILENT').setName('SILENT')
sparqlparser.addElement(SILENT_p)

GRAPH_p = CaselessKeyword('GRAPH').setName('GRAPH')
sparqlparser.addElement(GRAPH_p)

OPTIONAL_p = CaselessKeyword('OPTIONAL').setName('OPTIONAL')
sparqlparser.addElement(OPTIONAL_p)

DEFAULT_p = CaselessKeyword('DEFAULT').setName('DEFAULT')
sparqlparser.addElement(DEFAULT_p)

NAMED_p = CaselessKeyword('NAMED').setName('NAMED')
sparqlparser.addElement(NAMED_p)

ALL_p = CaselessKeyword('ALL').setName('ALL')
sparqlparser.addElement(ALL_p)

USING_p = CaselessKeyword('USING').setName('USING')
sparqlparser.addElement(USING_p)

INSERT_p = CaselessKeyword('INSERT').setName('INSERT')
sparqlparser.addElement(INSERT_p)

DELETE_p = CaselessKeyword('DELETE').setName('DELETE')
sparqlparser.addElement(DELETE_p)

WITH_p = CaselessKeyword('WITH').setName('WITH')
sparqlparser.addElement(WITH_p)

WHERE_p = CaselessKeyword('WHERE').setName('WHERE')
sparqlparser.addElement(WHERE_p)

DELETE_WHERE_p = (CaselessKeyword('DELETE') + CaselessKeyword('WHERE')).setName('DELETE_WHERE')
sparqlparser.addElement(DELETE_WHERE_p)

DELETE_DATA_p = (CaselessKeyword('DELETE') + CaselessKeyword('DATA')).setName('DELETE_DATA')
sparqlparser.addElement(DELETE_DATA_p)

INSERT_DATA_p = (CaselessKeyword('INSERT') + CaselessKeyword('DATA')).setName('INSERT_DATA')
sparqlparser.addElement(INSERT_DATA_p)

COPY_p = CaselessKeyword('COPY').setName('COPY')
sparqlparser.addElement(COPY_p)

MOVE_p = CaselessKeyword('MOVE').setName('MOVE')
sparqlparser.addElement(MOVE_p)

ADD_p = CaselessKeyword('ADD').setName('ADD')
sparqlparser.addElement(ADD_p)

CREATE_p = CaselessKeyword('CREATE').setName('CREATE')
sparqlparser.addElement(CREATE_p)

DROP_p = CaselessKeyword('DROP').setName('DROP')
sparqlparser.addElement(DROP_p)

CLEAR_p = CaselessKeyword('CLEAR').setName('CLEAR')
sparqlparser.addElement(CLEAR_p)

LOAD_p = CaselessKeyword('LOAD').setName('LOAD')
sparqlparser.addElement(LOAD_p)

TO_p = CaselessKeyword('TO').setName('TO')
sparqlparser.addElement(TO_p)

INTO_p = CaselessKeyword('INTO').setName('INTO')
sparqlparser.addElement(INTO_p)

OFFSET_p = CaselessKeyword('OFFSET').setName('OFFSET')
sparqlparser.addElement(OFFSET_p)

LIMIT_p = CaselessKeyword('LIMIT').setName('LIMIT')
sparqlparser.addElement(LIMIT_p)

ASC_p = CaselessKeyword('ASC').setName('ASC')
sparqlparser.addElement(ASC_p)

DESC_p = CaselessKeyword('DESC').setName('DESC')
sparqlparser.addElement(DESC_p)

ORDER_BY_p = (CaselessKeyword('ORDER') + CaselessKeyword('BY')).setName('ORDER_BY')
sparqlparser.addElement(ORDER_BY_p)

HAVING_p = CaselessKeyword('HAVING').setName('HAVING')
sparqlparser.addElement(HAVING_p)

GROUP_BY_p = (CaselessKeyword('GROUP') + CaselessKeyword('BY')).setName('GROUP_BY')
sparqlparser.addElement(GROUP_BY_p)

FROM_p = CaselessKeyword('FROM').setName('FROM')
sparqlparser.addElement(FROM_p)

ASK_p = CaselessKeyword('ASK').setName('ASK')
sparqlparser.addElement(ASK_p)

DESCRIBE_p = CaselessKeyword('DESCRIBE').setName('DESCRIBE')
sparqlparser.addElement(DESCRIBE_p)

CONSTRUCT_p = CaselessKeyword('CONSTRUCT').setName('CONSTRUCT')
sparqlparser.addElement(CONSTRUCT_p)

SELECT_p = CaselessKeyword('SELECT').setName('SELECT')
sparqlparser.addElement(SELECT_p)

REDUCED_p = CaselessKeyword('REDUCED').setName('REDUCED')
sparqlparser.addElement(REDUCED_p)

PREFIX_p = CaselessKeyword('PREFIX').setName('PREFIX')
sparqlparser.addElement(PREFIX_p)

BASE_p = CaselessKeyword('BASE').setName('BASE')
sparqlparser.addElement(BASE_p)

# 
# Parsers and classes for terminals
#

# [173]   PN_LOCAL_ESC      ::=   '\' ( '_' | '~' | '.' | '-' | '!' | '$' | '&' | "'" | '(' | ')' | '*' | '+' | ',' | ';' | '=' | '/' | '?' | '#' | '@' | '%' ) 
PN_LOCAL_ESC_e = r'\\[_~.\-!$&\'()*+,;=/?#@%]'
PN_LOCAL_ESC_p = Regex(PN_LOCAL_ESC_e).setName('PN_LOCAL_ESC')
sparqlparser.addElement(PN_LOCAL_ESC_p)


# [172]   HEX       ::=   [0-9] | [A-F] | [a-f] 
HEX_e = r'[0-9A-Fa-f]'
HEX_p = Regex(HEX_e).setName('HEX')
sparqlparser.addElement(HEX_p)

# [171]   PERCENT   ::=   '%' HEX HEX
PERCENT_e = r'%({})({})'.format( HEX_e, HEX_e)
PERCENT_p = Regex(PERCENT_e).setName('PERCENT')
sparqlparser.addElement(PERCENT_p)

# [170]   PLX       ::=   PERCENT | PN_LOCAL_ESC 
PLX_e = r'({})|({})'.format( PERCENT_e, PN_LOCAL_ESC_e)
PLX_p = Regex(PLX_e).setName('PLX')
sparqlparser.addElement(PLX_p)

# [164]   PN_CHARS_BASE     ::=   [A-Z] | [a-z] | [#x00C0-#x00D6] | [#x00D8-#x00F6] | [#x00F8-#x02FF] | [#x0370-#x037D] | [#x037F-#x1FFF] | [#x200C-#x200D] | [#x2070-#x218F] | [#x2C00-#x2FEF] | [#x3001-#xD7FF] | [#xF900-#xFDCF] | [#xFDF0-#xFFFD] | [#x10000-#xEFFFF] 
PN_CHARS_BASE_e = r'[A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\U00010000-\U000EFFFF]'
PN_CHARS_BASE_p = Regex(PN_CHARS_BASE_e).setName('PN_CHARS_BASE')
sparqlparser.addElement(PN_CHARS_BASE_p)

# [165]   PN_CHARS_U        ::=   PN_CHARS_BASE | '_' 
PN_CHARS_U_e = r'({})|({})'.format( PN_CHARS_BASE_e, r'_')
PN_CHARS_U_p = Regex(PN_CHARS_U_e).setName('PN_CHARS_U')
sparqlparser.addElement(PN_CHARS_U_p)

# [167]   PN_CHARS          ::=   PN_CHARS_U | '-' | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] 
PN_CHARS_e = r'({})|({})|({})|({})|({})|({})'.format( PN_CHARS_U_e, r'\-', r'[0-9]',  r'\u00B7', r'[\u0300-\u036F]', r'[\u203F-\u2040]')
PN_CHARS_p = Regex(PN_CHARS_e).setName('PN_CHARS')
sparqlparser.addElement(PN_CHARS_p)

# [169]   PN_LOCAL          ::=   (PN_CHARS_U | ':' | [0-9] | PLX ) ((PN_CHARS | '.' | ':' | PLX)* (PN_CHARS | ':' | PLX) )?
PN_LOCAL_e = r'(({})|({})|({})|({}))((({})|({})|({})|({}))*(({})|({})|({})))?'.format( PN_CHARS_U_e, r':', r'[0-9]', PLX_e, PN_CHARS_e, r'\.', r':', PLX_e, PN_CHARS_e, r':', PLX_e) 
PN_LOCAL_p = Regex(PN_LOCAL_e).setName('PN_LOCAL')
sparqlparser.addElement(PN_LOCAL_p)
            
# [168]   PN_PREFIX         ::=   PN_CHARS_BASE ((PN_CHARS|'.')* PN_CHARS)?
PN_PREFIX_e = r'({})((({})|({}))*({}))?'.format( PN_CHARS_BASE_e, PN_CHARS_e, r'\.', PN_CHARS_e)
PN_PREFIX_p = Regex(PN_PREFIX_e).setName('PN_PREFIX')
sparqlparser.addElement(PN_PREFIX_p)

# [166]   VARNAME   ::=   ( PN_CHARS_U | [0-9] ) ( PN_CHARS_U | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] )* 
VARNAME_e = r'(({})|({}))(({})|({})|({})|({})|({}))*'.format( PN_CHARS_U_e, r'[0-9]', PN_CHARS_U_e, r'[0-9]', r'\u00B7', r'[\u0030-036F]', r'[\u0203-\u2040]')
VARNAME_p = Regex(VARNAME_e).setName('VARNAME')
sparqlparser.addElement(VARNAME_p)

# [163]   ANON      ::=   '[' WS* ']' 
ANON_p = Group(Literal('[') + Literal(']')).setName('ANON')
sparqlparser.addElement(ANON_p)

# [162]   WS        ::=   #x20 | #x9 | #xD | #xA 
# WS is not used
# In the SPARQL EBNF this production is used for defining NIL and ANON, but in this pyparsing implementation those are implemented differently

# [161]   NIL       ::=   '(' WS* ')' 
NIL_p = Group(Literal('(') + Literal(')')).setName('NIL')
sparqlparser.addElement(NIL_p)

# [160]   ECHAR     ::=   '\' [tbnrf\"']
ECHAR_e = r'\\[tbnrf\\"\']'
ECHAR_p = Regex(ECHAR_e).setName('ECHAR')
sparqlparser.addElement(ECHAR_p)
 
# [159]   STRING_LITERAL_LONG2      ::=   '"""' ( ( '"' | '""' )? ( [^"\] | ECHAR ) )* '"""'  
STRING_LITERAL_LONG2_e = r'"""((""|")?(({})|({})))*"""'.format(r'[^"\\]', ECHAR_e)
STRING_LITERAL_LONG2_p = Regex(STRING_LITERAL_LONG2_e).parseWithTabs().setName('STRING_LITERAL_LONG2')
sparqlparser.addElement(STRING_LITERAL_LONG2_p)

# [158]   STRING_LITERAL_LONG1      ::=   "'''" ( ( "'" | "''" )? ( [^'\] | ECHAR ) )* "'''" 
STRING_LITERAL_LONG1_e = r"'''(('|'')?(({})|({})))*'''".format(r"[^'\\]", ECHAR_e)
STRING_LITERAL_LONG1_p = Regex(STRING_LITERAL_LONG1_e).parseWithTabs().setName('STRING_LITERAL_LONG1')
sparqlparser.addElement(STRING_LITERAL_LONG1_p)

# [157]   STRING_LITERAL2   ::=   '"' ( ([^#x22#x5C#xA#xD]) | ECHAR )* '"' 
STRING_LITERAL2_e = r'"(({})|({}))*"'.format(ECHAR_e, r'[^\u0022\u005C\u000A\u000D]')
STRING_LITERAL2_p = Regex(STRING_LITERAL2_e).parseWithTabs().setName('STRING_LITERAL2')
sparqlparser.addElement(STRING_LITERAL2_p)
                           
# [156]   STRING_LITERAL1   ::=   "'" ( ([^#x27#x5C#xA#xD]) | ECHAR )* "'" 
STRING_LITERAL1_e = r"'(({})|({}))*'".format(ECHAR_e, r'[^\u0027\u005C\u000A\u000D]')
STRING_LITERAL1_p = Regex(STRING_LITERAL1_e).parseWithTabs().setName('STRING_LITERAL1')
sparqlparser.addElement(STRING_LITERAL1_p)
                            
# [155]   EXPONENT          ::=   [eE] [+-]? [0-9]+ 
EXPONENT_e = r'[eE][+-][0-9]+'
EXPONENT_p = Regex(EXPONENT_e).setName('EXPONENT')
sparqlparser.addElement(EXPONENT_p)

# [148]   DOUBLE    ::=   [0-9]+ '.' [0-9]* EXPONENT | '.' ([0-9])+ EXPONENT | ([0-9])+ EXPONENT 
DOUBLE_e = r'([0-9]+\.[0-9]*({}))|(\.[0-9]+({}))|([0-9]+({}))'.format(EXPONENT_e, EXPONENT_e, EXPONENT_e)
DOUBLE_p = Regex(DOUBLE_e).setName('DOUBLE')
sparqlparser.addElement(DOUBLE_p)

# [154]   DOUBLE_NEGATIVE   ::=   '-' DOUBLE 
DOUBLE_NEGATIVE_e = r'\-({})'.format(DOUBLE_e)
DOUBLE_NEGATIVE_p = Regex(DOUBLE_NEGATIVE_e).setName('DOUBLE_NEGATIVE')
sparqlparser.addElement(DOUBLE_NEGATIVE_p)

# [151]   DOUBLE_POSITIVE   ::=   '+' DOUBLE 
DOUBLE_POSITIVE_e = r'\+({})'.format(DOUBLE_e)
DOUBLE_POSITIVE_p = Regex(DOUBLE_POSITIVE_e).setName('DOUBLE_POSITIVE')
sparqlparser.addElement(DOUBLE_POSITIVE_p)

# [147]   DECIMAL   ::=   [0-9]* '.' [0-9]+ 
DECIMAL_e = r'[0-9]*\.[0-9]+'
DECIMAL_p = Regex(DECIMAL_e).setName('DECIMAL')
sparqlparser.addElement(DECIMAL_p)

# [153]   DECIMAL_NEGATIVE          ::=   '-' DECIMAL 
DECIMAL_NEGATIVE_e = r'\-({})'.format(DECIMAL_e)
DECIMAL_NEGATIVE_p = Regex(DECIMAL_NEGATIVE_e).setName('DECIMAL_NEGATIVE')
sparqlparser.addElement(DECIMAL_NEGATIVE_p)

# [150]   DECIMAL_POSITIVE          ::=   '+' DECIMAL 
DECIMAL_POSITIVE_e = r'\+({})'.format(DECIMAL_e)
DECIMAL_POSITIVE_p = Regex(DECIMAL_POSITIVE_e).setName('DECIMAL_POSITIVE')
sparqlparser.addElement(DECIMAL_POSITIVE_p)

# [146]   INTEGER   ::=   [0-9]+ 
INTEGER_e = r'[0-9]+'
INTEGER_p = Regex(INTEGER_e).setName('INTEGER')
sparqlparser.addElement(INTEGER_p)

# [152]   INTEGER_NEGATIVE          ::=   '-' INTEGER
INTEGER_NEGATIVE_e = r'\-({})'.format(INTEGER_e)
INTEGER_NEGATIVE_p = Regex(INTEGER_NEGATIVE_e).setName('INTEGER_NEGATIVE')
sparqlparser.addElement(INTEGER_NEGATIVE_p)

# [149]   INTEGER_POSITIVE          ::=   '+' INTEGER 
INTEGER_POSITIVE_e = r'\+({})'.format(INTEGER_e)
INTEGER_POSITIVE_p = Regex(INTEGER_POSITIVE_e).setName('INTEGER_POSITIVE')
sparqlparser.addElement(INTEGER_POSITIVE_p)

# [145]   LANGTAG   ::=   '@' [a-zA-Z]+ ('-' [a-zA-Z0-9]+)* 
LANGTAG_e = r'@[a-zA-Z]+(\-[a-zA-Z0-9]+)*'
LANGTAG_p = Regex(LANGTAG_e).setName('LANGTAG')
sparqlparser.addElement(LANGTAG_p)

# [144]   VAR2      ::=   '$' VARNAME 
VAR2_e = r'\$({})'.format(VARNAME_e)
VAR2_p = Regex(VAR2_e).setName('VAR2')
sparqlparser.addElement(VAR2_p)

# [143]   VAR1      ::=   '?' VARNAME 
VAR1_e = r'\?({})'.format(VARNAME_e)
VAR1_p = Regex(VAR1_e).setName('VAR1')
sparqlparser.addElement(VAR1_p)

# [142]   BLANK_NODE_LABEL          ::=   '_:' ( PN_CHARS_U | [0-9] ) ((PN_CHARS|'.')* PN_CHARS)?
BLANK_NODE_LABEL_e = r'_:(({})|[0-9])((({})|\.)*({}))?'.format(PN_CHARS_U_e, PN_CHARS_e, PN_CHARS_e)
BLANK_NODE_LABEL_p = Regex(BLANK_NODE_LABEL_e).setName('BLANK_NODE_LABEL')
sparqlparser.addElement(BLANK_NODE_LABEL_p)

# [140]   PNAME_NS          ::=   PN_PREFIX? ':'
PNAME_NS_e = r'({})?:'.format(PN_PREFIX_e)
PNAME_NS_p = Regex(PNAME_NS_e).setName('PNAME_NS')
sparqlparser.addElement(PNAME_NS_p)

# [141]   PNAME_LN          ::=   PNAME_NS PN_LOCAL 
PNAME_LN_e = r'({})({})'.format(PNAME_NS_e, PN_LOCAL_e)
PNAME_LN_p = Regex(PNAME_LN_e).setName('PNAME_LN')
sparqlparser.addElement(PNAME_LN_p)

# [139]   IRIREF    ::=   '<' ([^<>"{}|^`\]-[#x00-#x20])* '>' 
IRIREF_e = r'<[^<>"{}|^`\\\\\u0000-\u0020]*>'
IRIREF_p = Regex(IRIREF_e).setName('IRIREF')
sparqlparser.addElement(IRIREF_p)

#
# Parsers and classes for non-terminals
#

# [138]   BlankNode         ::=   BLANK_NODE_LABEL | ANON 
BlankNode_p = Group(BLANK_NODE_LABEL_p | ANON_p).setName('BlankNode')
sparqlparser.addElement(BlankNode_p)

# [137]   PrefixedName      ::=   PNAME_LN | PNAME_NS 
PrefixedName_p = Group(PNAME_LN_p ^ PNAME_NS_p).setName('PrefixedName')
sparqlparser.addElement(PrefixedName_p)

# [136]   iri       ::=   IRIREF | PrefixedName 
iri_p = Group(IRIREF_p ^ PrefixedName_p).setName('iri')
sparqlparser.addElement(iri_p)

# [135]   String    ::=   STRING_LITERAL1 | STRING_LITERAL2 | STRING_LITERAL_LONG1 | STRING_LITERAL_LONG2 
String_p = Group(STRING_LITERAL1_p ^ STRING_LITERAL2_p ^ STRING_LITERAL_LONG1_p ^ STRING_LITERAL_LONG2_p).setName('String')
sparqlparser.addElement(String_p)
 
# [134]   BooleanLiteral    ::=   'true' | 'false' 
BooleanLiteral_p = Group(Literal('true') | Literal('false')).setName('BooleanLiteral')
sparqlparser.addElement(BooleanLiteral_p)
 
# [133]   NumericLiteralNegative    ::=   INTEGER_NEGATIVE | DECIMAL_NEGATIVE | DOUBLE_NEGATIVE 
NumericLiteralNegative_p = Group(INTEGER_NEGATIVE_p ^ DECIMAL_NEGATIVE_p ^ DOUBLE_NEGATIVE_p).setName('NumericLiteralNegative')
sparqlparser.addElement(NumericLiteralNegative_p)
 
# [132]   NumericLiteralPositive    ::=   INTEGER_POSITIVE | DECIMAL_POSITIVE | DOUBLE_POSITIVE 
NumericLiteralPositive_p = Group(INTEGER_POSITIVE_p ^ DECIMAL_POSITIVE_p ^ DOUBLE_POSITIVE_p).setName('NumericLiteralPositive')
sparqlparser.addElement(NumericLiteralPositive_p)
 
# [131]   NumericLiteralUnsigned    ::=   INTEGER | DECIMAL | DOUBLE 
NumericLiteralUnsigned_p = Group(INTEGER_p ^ DECIMAL_p ^ DOUBLE_p).setName('NumericLiteralUnsigned')
sparqlparser.addElement(NumericLiteralUnsigned_p)

# # [130]   NumericLiteral    ::=   NumericLiteralUnsigned | NumericLiteralPositive | NumericLiteralNegative 
NumericLiteral_p = Group(NumericLiteralUnsigned_p | NumericLiteralPositive_p | NumericLiteralNegative_p).setName('NumericLiteral')
sparqlparser.addElement(NumericLiteral_p)

# [129]   RDFLiteral        ::=   String ( LANGTAG | ( '^^' iri ) )? 
RDFLiteral_p = Group(String_p('lexical_form') + Optional(Group ((LANGTAG_p('langtag') ^ ('^^' + iri_p('datatype_uri')))))).setName('RDFLiteral')
sparqlparser.addElement(RDFLiteral_p)

Expression_p = Forward().setName('Expression')
sparqlparser.addElement(Expression_p)

# [71]    ArgList   ::=   NIL | '(' 'DISTINCT'? Expression ( ',' Expression )* ')' 
ArgList_p = Group((NIL_p('nil')) | (LPAR_p + Optional(DISTINCT_p)('distinct') + separatedList(Expression_p)('argument') + RPAR_p)).setName('ArgList')
sparqlparser.addElement(ArgList_p)


# [128]   iriOrFunction     ::=   iri ArgList? 
iriOrFunction_p = Group(iri_p('iri') + Optional(ArgList_p)('argList')).setName('iriOrFunction')
sparqlparser.addElement(iriOrFunction_p)

# [127]   Aggregate         ::=     'COUNT' '(' 'DISTINCT'? ( '*' | Expression ) ')' 
#             | 'SUM' '(' 'DISTINCT'? Expression ')' 
#             | 'MIN' '(' 'DISTINCT'? Expression ')' 
#             | 'MAX' '(' 'DISTINCT'? Expression ')' 
#             | 'AVG' '(' 'DISTINCT'? Expression ')' 
#             | 'SAMPLE' '(' 'DISTINCT'? Expression ')' 
#             | 'GROUP_CONCAT' '(' 'DISTINCT'? Expression ( ';' 'SEPARATOR' '=' String )? ')' 
Aggregate_p = Group((COUNT_p('count') + LPAR_p + Optional(DISTINCT_p('distinct')) + ( ALL_VALUES_p('all') ^ Expression_p('expression') ) + RPAR_p ) | \
            ( SUM_p('sum') + LPAR_p + Optional(DISTINCT_p('distinct')) + ( ALL_VALUES_p('all') ^ Expression_p('expression') ) + RPAR_p ) | \
            ( MIN_p('min') + LPAR_p + Optional(DISTINCT_p('distinct')) + ( ALL_VALUES_p('all') ^ Expression_p('expression') ) + RPAR_p ) | \
            ( MAX_p('max') + LPAR_p + Optional(DISTINCT_p('distinct')) + ( ALL_VALUES_p('all') ^ Expression_p('expression') ) + RPAR_p ) | \
            ( AVG_p('avg') + LPAR_p + Optional(DISTINCT_p('distinct')) + ( ALL_VALUES_p('all') ^ Expression_p('expression') ) + RPAR_p ) | \
            ( SAMPLE_p('sample') + LPAR_p + Optional(DISTINCT_p('distinct')) + ( ALL_VALUES_p('all') ^ Expression_p('expression') ) + RPAR_p ) | \
            ( GROUP_CONCAT_p('group_concat') + LPAR_p + Optional(DISTINCT_p('distinct')) + Expression_p('expression') + Optional( SEMICOL_p + SEPARATOR_p + '=' + String_p('separator') ) + RPAR_p)).setName('Aggregate')
sparqlparser.addElement(Aggregate_p)

GroupGraphPattern_p = Forward().setName('GroupGraphPattern')
sparqlparser.addElement(GroupGraphPattern_p)
 
# [126]   NotExistsFunc     ::=   'NOT' 'EXISTS' GroupGraphPattern 
NotExistsFunc_p = Group(NOT_EXISTS_p + GroupGraphPattern_p('groupgraph')).setName('NotExistsFunc')
sparqlparser.addElement(NotExistsFunc_p)
 
# [125]   ExistsFunc        ::=   'EXISTS' GroupGraphPattern 
ExistsFunc_p = Group(EXISTS_p + GroupGraphPattern_p('groupgraph')).setName('ExistsFunc')
sparqlparser.addElement(ExistsFunc_p)
 
# [124]   StrReplaceExpression      ::=   'REPLACE' '(' Expression ',' Expression ',' Expression ( ',' Expression )? ')' 
StrReplaceExpression_p = Group(REPLACE_p + LPAR_p + Expression_p('arg') + COMMA_p + Expression_p('pattern') + COMMA_p + Expression_p('replacement') + Optional(COMMA_p + Expression_p('flags')) + RPAR_p).setName('StrReplaceExpression')
sparqlparser.addElement(StrReplaceExpression_p)
 
# [123]   SubstringExpression       ::=   'SUBSTR' '(' Expression ',' Expression ( ',' Expression )? ')' 
SubstringExpression_p = Group(SUBSTR_p + LPAR_p + Expression_p('source') + COMMA_p + Expression_p('startloc') + Optional(COMMA_p + Expression_p('length')) + RPAR_p).setName('SubstringExpression')
sparqlparser.addElement(SubstringExpression_p)
 
# [122]   RegexExpression   ::=   'REGEX' '(' Expression ',' Expression ( ',' Expression )? ')' 
RegexExpression_p = Group(REGEX_p + LPAR_p + Expression_p('text') + COMMA_p + Expression_p('pattern') + Optional(COMMA_p + Expression_p('flags')) + RPAR_p).setName('RegexExpression')
sparqlparser.addElement(RegexExpression_p)

# [108]   Var       ::=   VAR1 | VAR2 
Var_p = Group(VAR1_p | VAR2_p).setName('Var')
sparqlparser.addElement(Var_p)

ExpressionList_p = Forward().setName('ExpressionList')
sparqlparser.addElement(ExpressionList_p)


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
                STR_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                LANG_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                LANGMATCHES_p + LPAR_p + Expression_p('language-tag') + COMMA_p + Expression_p('language-range') + RPAR_p    | \
                DATATYPE_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                BOUND_p + LPAR_p + Var_p('var') + RPAR_p    | \
                IRI_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                URI_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                BNODE_p + (LPAR_p + Expression_p('expression') + RPAR_p | NIL_p)    | \
                RAND_p + NIL_p    | \
                ABS_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                CEIL_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                FLOOR_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                ROUND_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                CONCAT_p + ExpressionList_p('expressionList')    | \
                SubstringExpression_p   | \
                STRLEN_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                StrReplaceExpression_p  | \
                UCASE_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                LCASE_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                ENCODE_FOR_URI_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                CONTAINS_p + LPAR_p + Expression_p('arg1') + COMMA_p + Expression_p('arg2') + RPAR_p    | \
                STRSTARTS_p + LPAR_p + Expression_p('arg1') + COMMA_p + Expression_p('arg2') + RPAR_p    | \
                STRENDS_p + LPAR_p + Expression_p('arg1') + COMMA_p + Expression_p('arg2') + RPAR_p    | \
                STRBEFORE_p + LPAR_p + Expression_p('arg1') + COMMA_p + Expression_p('arg2') + RPAR_p    | \
                STRAFTER_p + LPAR_p + Expression_p('arg1') + COMMA_p + Expression_p('arg2') + RPAR_p    | \
                YEAR_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                MONTH_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                DAY_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                HOURS_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                MINUTES_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                SECONDS_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                TIMEZONE_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                TZ_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                NOW_p + NIL_p    | \
                UUID_p + NIL_p    | \
                STRUUID_p + NIL_p    | \
                MD5_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                SHA1_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                SHA256_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                SHA384_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                SHA512_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                COALESCE_p + ExpressionList_p('expressionList')    | \
                IF_p + LPAR_p + Expression_p('expression1') + COMMA_p + Expression_p('expression2') + COMMA_p + Expression_p('expression3') + RPAR_p    | \
                STRLANG_p + LPAR_p + Expression_p('lexicalForm') + COMMA_p + Expression_p('langTag') + RPAR_p    | \
                STRDT_p + LPAR_p + Expression_p('lexicalForm') + COMMA_p + Expression_p('datatypeIRI') + RPAR_p    | \
                sameTerm_p + LPAR_p + Expression_p('term1') + COMMA_p + Expression_p('term2') + RPAR_p    | \
                isIRI_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                isURI_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                isBLANK_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                isLITERAL_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                isNUMERIC_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                RegexExpression_p | \
                ExistsFunc_p | \
                NotExistsFunc_p ).setName('BuiltInCall')
sparqlparser.addElement(BuiltInCall_p)

# [120]   BrackettedExpression      ::=   '(' Expression ')' 
BracketedExpression_p = Group(LPAR_p + Expression_p('expression') + RPAR_p).setName('BracketedExpression')
sparqlparser.addElement(BracketedExpression_p)

# [119]   PrimaryExpression         ::=   BrackettedExpression | BuiltInCall | iriOrFunction | RDFLiteral | NumericLiteral | BooleanLiteral | Var 
PrimaryExpression_p = Group(BracketedExpression_p | BuiltInCall_p | iriOrFunction_p('iriOrFunction') | RDFLiteral_p | NumericLiteral_p | BooleanLiteral_p | Var_p).setName('PrimaryExpression')
sparqlparser.addElement(PrimaryExpression_p)

# [118]   UnaryExpression   ::=     '!' PrimaryExpression 
#             | '+' PrimaryExpression 
#             | '-' PrimaryExpression 
#             | PrimaryExpression 
UnaryExpression_p = Group(NEGATE_p + PrimaryExpression_p | PLUS_p + PrimaryExpression_p | MINUS_p + PrimaryExpression_p | PrimaryExpression_p).setName('UnaryExpression')
sparqlparser.addElement(UnaryExpression_p)

# [117]   MultiplicativeExpression          ::=   UnaryExpression ( '*' UnaryExpression | '/' UnaryExpression )* 
MultiplicativeExpression_p = Group(UnaryExpression_p + ZeroOrMore( TIMES_p + UnaryExpression_p | DIV_p + UnaryExpression_p )).setName('MultiplicativeExpression')
sparqlparser.addElement(MultiplicativeExpression_p)

# [116]   AdditiveExpression        ::=   MultiplicativeExpression ( '+' MultiplicativeExpression | '-' MultiplicativeExpression | ( NumericLiteralPositive | NumericLiteralNegative ) ( ( '*' UnaryExpression ) | ( '/' UnaryExpression ) )* )* 
AdditiveExpression_p = Group(MultiplicativeExpression_p + ZeroOrMore (PLUS_p + MultiplicativeExpression_p | MINUS_p  + MultiplicativeExpression_p | (NumericLiteralPositive_p | NumericLiteralNegative_p) + ZeroOrMore (TIMES_p + UnaryExpression_p | DIV_p + UnaryExpression_p))).setName('AdditiveExpression')
sparqlparser.addElement(AdditiveExpression_p)

# [115]   NumericExpression         ::=   AdditiveExpression 
NumericExpression_p = Group(AdditiveExpression_p + Empty()).setName('NumericExpression')
sparqlparser.addElement(NumericExpression_p)

# [114]   RelationalExpression      ::=   NumericExpression ( '=' NumericExpression | '!=' NumericExpression | '<' NumericExpression | '>' NumericExpression | '<=' NumericExpression | '>=' NumericExpression | 'IN' ExpressionList | 'NOT' 'IN' ExpressionList )? 
RelationalExpression_p = Group(NumericExpression_p + Optional( EQ_p + NumericExpression_p | \
                                                         NE_p + NumericExpression_p | \
                                                         LT_p + NumericExpression_p | \
                                                         GT_p + NumericExpression_p | \
                                                         LE_p + NumericExpression_p | \
                                                         GE_p + NumericExpression_p | \
                                                         IN_p + ExpressionList_p | \
                                                         NOT_IN_p + ExpressionList_p) ).setName('RelationalExpression')
sparqlparser.addElement(RelationalExpression_p)

# [113]   ValueLogical      ::=   RelationalExpression 
ValueLogical_p = Group(RelationalExpression_p + Empty()).setName('ValueLogical')
sparqlparser.addElement(ValueLogical_p)

# [112]   ConditionalAndExpression          ::=   ValueLogical ( '&&' ValueLogical )* 
ConditionalAndExpression_p = Group(ValueLogical_p + ZeroOrMore(AND_p + ValueLogical_p)).setName('ConditionalAndExpression')
sparqlparser.addElement(ConditionalAndExpression_p)

# [111]   ConditionalOrExpression   ::=   ConditionalAndExpression ( '||' ConditionalAndExpression )* 
ConditionalOrExpression_p = Group(ConditionalAndExpression_p + ZeroOrMore(OR_p + ConditionalAndExpression_p)).setName('ConditionalOrExpression')
sparqlparser.addElement(ConditionalOrExpression_p)

# [110]   Expression        ::=   ConditionalOrExpression 
Expression_p << Group(ConditionalOrExpression_p + Empty())

# [109]   GraphTerm         ::=   iri | RDFLiteral | NumericLiteral | BooleanLiteral | BlankNode | NIL 
GraphTerm_p =   Group(iri_p | \
                RDFLiteral_p | \
                NumericLiteral_p | \
                BooleanLiteral_p | \
                BlankNode_p | \
                NIL_p ).setName('GraphTerm')
sparqlparser.addElement(GraphTerm_p)
                
# [107]   VarOrIri          ::=   Var | iri 
VarOrIri_p = Group(Var_p | iri_p).setName('VarOrIri')
sparqlparser.addElement(VarOrIri_p)

# [106]   VarOrTerm         ::=   Var | GraphTerm 
VarOrTerm_p = Group(Var_p | GraphTerm_p).setName('VarOrTerm')
sparqlparser.addElement(VarOrTerm_p)

TriplesNodePath_p = Forward().setName('TriplesNodePath')
sparqlparser.addElement(TriplesNodePath_p)

# [105]   GraphNodePath     ::=   VarOrTerm | TriplesNodePath 
GraphNodePath_p = Group(VarOrTerm_p ^ TriplesNodePath_p ).setName('GraphNodePath')
sparqlparser.addElement(GraphNodePath_p)

TriplesNode_p = Forward().setName('TriplesNode')
sparqlparser.addElement(TriplesNode_p)

# [104]   GraphNode         ::=   VarOrTerm | TriplesNode 
GraphNode_p = Group(VarOrTerm_p ^ TriplesNode_p).setName('GraphNode')
sparqlparser.addElement(GraphNode_p)

# [103]   CollectionPath    ::=   '(' GraphNodePath+ ')' 
CollectionPath_p = Group(LPAR_p + OneOrMore(GraphNodePath_p) + RPAR_p).setName('CollectionPath')
sparqlparser.addElement(CollectionPath_p)

# [102]   Collection        ::=   '(' GraphNode+ ')' 
Collection_p = Group(LPAR_p + OneOrMore(GraphNode_p) + RPAR_p).setName('Collection')
sparqlparser.addElement(Collection_p)

PropertyListPathNotEmpty_p = Forward().setName('PropertyListPathNotEmpty')
sparqlparser.addElement(PropertyListPathNotEmpty_p)

# [101]   BlankNodePropertyListPath         ::=   '[' PropertyListPathNotEmpty ']'
BlankNodePropertyListPath_p = Group(LBRACK_p + PropertyListPathNotEmpty_p + RBRACK_p ).setName('BlankNodePropertyListPath')
sparqlparser.addElement(BlankNodePropertyListPath_p)

# [100]   TriplesNodePath   ::=   CollectionPath | BlankNodePropertyListPath 
TriplesNodePath_p << Group(CollectionPath_p | BlankNodePropertyListPath_p)

PropertyListNotEmpty_p = Forward().setName('PropertyListNotEmpty')
sparqlparser.addElement(PropertyListNotEmpty_p)

# [99]    BlankNodePropertyList     ::=   '[' PropertyListNotEmpty ']' 
BlankNodePropertyList_p = Group(LBRACK_p + PropertyListNotEmpty_p + RBRACK_p ).setName('BlankNodePropertyList')
sparqlparser.addElement(BlankNodePropertyList_p)

# [98]    TriplesNode       ::=   Collection | BlankNodePropertyList 
TriplesNode_p << Group(Collection_p | BlankNodePropertyList_p)

# [97]    Integer   ::=   INTEGER 
Integer_p = Group(INTEGER_p + Empty()).setName('Integer')
sparqlparser.addElement(Integer_p)

# [96]    PathOneInPropertySet      ::=   iri | 'a' | '^' ( iri | 'a' ) 
PathOneInPropertySet_p = Group(iri_p | TYPE_p | (INVERSE_p  + ( iri_p | TYPE_p ))).setName('PathOneInPropertySet')
sparqlparser.addElement(PathOneInPropertySet_p)

# [95]    PathNegatedPropertySet    ::=   PathOneInPropertySet | '(' ( PathOneInPropertySet ( '|' PathOneInPropertySet )* )? ')' 
PathNegatedPropertySet_p = Group(PathOneInPropertySet_p | (LPAR_p + Group(Optional(separatedList(PathOneInPropertySet_p, sep='|'))('pathinonepropertyset')) + RPAR_p)).setName('PathNegatedPropertySet')
sparqlparser.addElement(PathNegatedPropertySet_p)

Path_p = Forward().setName('Path')
sparqlparser.addElement(Path_p)

# [94]    PathPrimary       ::=   iri | 'a' | '!' PathNegatedPropertySet | '(' Path ')' 
PathPrimary_p = Group(iri_p | TYPE_p | (NEGATE_p + PathNegatedPropertySet_p) | (LPAR_p + Path_p + RPAR_p)).setName('PathPrimary')
sparqlparser.addElement(PathPrimary_p)

# [93]    PathMod   ::=   '?' | '*' | '+' 
PathMod_p = Group((~VAR1_p + Literal('?')) | Literal('*') | Literal('+')).setName('PathMod')
sparqlparser.addElement(PathMod_p)

# [91]    PathElt   ::=   PathPrimary PathMod? 
PathElt_p = Group(PathPrimary_p + Optional(PathMod_p) ).setName('PathElt')
sparqlparser.addElement(PathElt_p)

# [92]    PathEltOrInverse          ::=   PathElt | '^' PathElt 
PathEltOrInverse_p = Group(PathElt_p | (INVERSE_p + PathElt_p)).setName('PathEltOrInverse')
sparqlparser.addElement(PathEltOrInverse_p)

# [90]    PathSequence      ::=   PathEltOrInverse ( '/' PathEltOrInverse )* 
PathSequence_p = Group(separatedList(PathEltOrInverse_p, sep='/')).setName('PathSequence')
sparqlparser.addElement(PathSequence_p)

# [89]    PathAlternative   ::=   PathSequence ( '|' PathSequence )* 
PathAlternative_p = Group(separatedList(PathSequence_p, sep='|')).setName('PathAlternative')
sparqlparser.addElement(PathAlternative_p)
 
# [88]    Path      ::=   PathAlternative
Path_p << Group(PathAlternative_p + Empty())

# [87]    ObjectPath        ::=   GraphNodePath 
ObjectPath_p = Group(GraphNodePath_p + Empty() ).setName('ObjectPath')
sparqlparser.addElement(ObjectPath_p)

# [86]    ObjectListPath    ::=   ObjectPath ( ',' ObjectPath )* 
ObjectListPath_p = Group(separatedList(ObjectPath_p)).setName('ObjectListPath')
sparqlparser.addElement(ObjectListPath_p)

# [85]    VerbSimple        ::=   Var 
VerbSimple_p = Group(Var_p + Empty() ).setName('VerbSimple')
sparqlparser.addElement(VerbSimple_p)

# [84]    VerbPath          ::=   Path
VerbPath_p = Group(Path_p + Empty() ).setName('VerbPath')
sparqlparser.addElement(VerbPath_p)

# [80]    Object    ::=   GraphNode 
Object_p = Group(GraphNode_p + Empty() ).setName('Object')
sparqlparser.addElement(Object_p)
 
# [79]    ObjectList        ::=   Object ( ',' Object )* 
ObjectList_p = Group(separatedList(Object_p)).setName('ObjectList')
sparqlparser.addElement(ObjectList_p)

# [83]    PropertyListPathNotEmpty          ::=   ( VerbPath | VerbSimple ) ObjectListPath ( ';' ( ( VerbPath | VerbSimple ) ObjectList )? )* 
PropertyListPathNotEmpty_p << Group((VerbPath_p | VerbSimple_p) + ObjectListPath_p +  ZeroOrMore(SEMICOL_p + Optional(( VerbPath_p | VerbSimple_p) + ObjectList_p)))

# [82]    PropertyListPath          ::=   PropertyListPathNotEmpty? 
PropertyListPath_p = Group(Optional(PropertyListPathNotEmpty_p)).setName('PropertyListPath')
sparqlparser.addElement(PropertyListPath_p)

# [81]    TriplesSameSubjectPath    ::=   VarOrTerm PropertyListPathNotEmpty | TriplesNodePath PropertyListPath 
TriplesSameSubjectPath_p = Group((VarOrTerm_p + PropertyListPathNotEmpty_p) | (TriplesNodePath_p + PropertyListPath_p)).setName('TriplesSameSubjectPath')
sparqlparser.addElement(TriplesSameSubjectPath_p)

# [78]    Verb      ::=   VarOrIri | 'a' 
Verb_p = Group(VarOrIri_p | TYPE_p).setName('Verb')
sparqlparser.addElement(Verb_p)

# [77]    PropertyListNotEmpty      ::=   Verb ObjectList ( ';' ( Verb ObjectList )? )* 
PropertyListNotEmpty_p << Group(Verb_p + ObjectList_p + ZeroOrMore(SEMICOL_p + Optional(Verb_p + ObjectList_p)))

# [76]    PropertyList      ::=   PropertyListNotEmpty?
PropertyList_p = Group(Optional(PropertyListNotEmpty_p) ).setName('PropertyList')
sparqlparser.addElement(PropertyList_p)

# [75]    TriplesSameSubject        ::=   VarOrTerm PropertyListNotEmpty | TriplesNode PropertyList
TriplesSameSubject_p = Group((VarOrTerm_p + PropertyListNotEmpty_p) | (TriplesNode_p + PropertyList_p) ).setName('TriplesSameSubject')
sparqlparser.addElement(TriplesSameSubject_p)

# [74]    ConstructTriples          ::=   TriplesSameSubject ( '.' ConstructTriples? )? 
ConstructTriples_p = Group(separatedList(TriplesSameSubject_p, sep='.') + Optional(PERIOD_p)).setName('ConstructTriples')
sparqlparser.addElement(ConstructTriples_p)

# [73]    ConstructTemplate         ::=   '{' ConstructTriples? '}'
ConstructTemplate_p = Group(LCURL_p + Optional(ConstructTriples_p) + RCURL_p ).setName('ConstructTemplate')
sparqlparser.addElement(ConstructTemplate_p)

# [72]    ExpressionList    ::=   NIL | '(' Expression ( ',' Expression )* ')' 
ExpressionList_p << Group(NIL_p | (LPAR_p + separatedList(Expression_p) + RPAR_p))

# [70]    FunctionCall      ::=   iri ArgList 
FunctionCall_p = Group(iri_p + ArgList_p).setName('FunctionCall')
sparqlparser.addElement(FunctionCall_p)

# [69]    Constraint        ::=   BrackettedExpression | BuiltInCall | FunctionCall 
Constraint_p = Group(BracketedExpression_p | BuiltInCall_p | FunctionCall_p).setName('Constraint')
sparqlparser.addElement(Constraint_p)

# [68]    Filter    ::=   'FILTER' Constraint
Filter_p = Group(FILTER_p + Constraint_p ).setName('Filter')
sparqlparser.addElement(Filter_p)

# [67]    GroupOrUnionGraphPattern          ::=   GroupGraphPattern ( 'UNION' GroupGraphPattern )* 
GroupOrUnionGraphPattern_p = Group(GroupGraphPattern_p + ZeroOrMore(UNION_p + GroupGraphPattern_p) ).setName('GroupOrUnionGraphPattern')
sparqlparser.addElement(GroupOrUnionGraphPattern_p)

# [66]    MinusGraphPattern         ::=   'MINUS' GroupGraphPattern
MinusGraphPattern_p = Group(SUBTRACT_p + GroupGraphPattern_p ).setName('MinusGraphPattern')
sparqlparser.addElement(MinusGraphPattern_p)

# [65]    DataBlockValue    ::=   iri | RDFLiteral | NumericLiteral | BooleanLiteral | 'UNDEF' 
DataBlockValue_p = Group(iri_p | RDFLiteral_p | NumericLiteral_p | BooleanLiteral_p | UNDEF_p).setName('DataBlockValue')
sparqlparser.addElement(DataBlockValue_p)

# [64]    InlineDataFull    ::=   ( NIL | '(' Var* ')' ) '{' ( '(' DataBlockValue* ')' | NIL )* '}' 
InlineDataFull_p = Group(( NIL_p | (LPAR_p + ZeroOrMore(Var_p) + RPAR_p)) + LCURL_p +  ZeroOrMore((LPAR_p + ZeroOrMore(DataBlockValue_p) + RPAR_p) | NIL_p) + RCURL_p ).setName('InlineDataFull')
sparqlparser.addElement(InlineDataFull_p)

# [63]    InlineDataOneVar          ::=   Var '{' DataBlockValue* '}' 
InlineDataOneVar_p = Group(Var_p + LCURL_p + ZeroOrMore(DataBlockValue_p) + RCURL_p ).setName('InlineDataOneVar')
sparqlparser.addElement(InlineDataOneVar_p)

# [62]    DataBlock         ::=   InlineDataOneVar | InlineDataFull 
DataBlock_p = Group(InlineDataOneVar_p | InlineDataFull_p).setName('DataBlock')
sparqlparser.addElement(DataBlock_p)

# [61]    InlineData        ::=   'VALUES' DataBlock 
InlineData_p = Group(VALUES_p + DataBlock_p ).setName('InlineData')
sparqlparser.addElement(InlineData_p)

# [60]    Bind      ::=   'BIND' '(' Expression 'AS' Var ')' 
Bind_p = Group(BIND_p + LPAR_p + Expression_p + AS_p + Var_p + RPAR_p ).setName('Bind')
sparqlparser.addElement(Bind_p)

# [59]    ServiceGraphPattern       ::=   'SERVICE' 'SILENT'? VarOrIri GroupGraphPattern 
ServiceGraphPattern_p = Group(SERVICE_p + Optional(SILENT_p) + VarOrIri_p + GroupGraphPattern_p ).setName('ServiceGraphPattern')
sparqlparser.addElement(ServiceGraphPattern_p)

# [58]    GraphGraphPattern         ::=   'GRAPH' VarOrIri GroupGraphPattern 
GraphGraphPattern_p = Group(GRAPH_p + VarOrIri_p + GroupGraphPattern_p ).setName('GraphGraphPattern')
sparqlparser.addElement(GraphGraphPattern_p)

# [57]    OptionalGraphPattern      ::=   'OPTIONAL' GroupGraphPattern 
OptionalGraphPattern_p = Group(OPTIONAL_p + GroupGraphPattern_p ).setName('OptionalGraphPattern')
sparqlparser.addElement(OptionalGraphPattern_p)

# [56]    GraphPatternNotTriples    ::=   GroupOrUnionGraphPattern | OptionalGraphPattern | MinusGraphPattern | GraphGraphPattern | ServiceGraphPattern | Filter | Bind | InlineData 
GraphPatternNotTriples_p = Group(GroupOrUnionGraphPattern_p | OptionalGraphPattern_p | MinusGraphPattern_p | GraphGraphPattern_p | ServiceGraphPattern_p | Filter_p | Bind_p | InlineData_p ).setName('GraphPatternNotTriples')
sparqlparser.addElement(GraphPatternNotTriples_p)
                                           
# [55]    TriplesBlock      ::=   TriplesSameSubjectPath ( '.' TriplesBlock? )? 
TriplesBlock_p = Group(separatedList(TriplesSameSubjectPath_p, sep='.')('subjpath') + Optional(PERIOD_p)).setName('TriplesBlock')
sparqlparser.addElement(TriplesBlock_p)

# [54]    GroupGraphPatternSub      ::=   TriplesBlock? ( GraphPatternNotTriples '.'? TriplesBlock? )* 
GroupGraphPatternSub_p = Group(Optional(TriplesBlock_p) + ZeroOrMore(GraphPatternNotTriples_p + Optional(PERIOD_p) + Optional(TriplesBlock_p)) ).setName('GroupGraphPatternSub')
sparqlparser.addElement(GroupGraphPatternSub_p)

SubSelect_p = Forward().setName('SubSelect')
sparqlparser.addElement(SubSelect_p)

# [53]    GroupGraphPattern         ::=   '{' ( SubSelect | GroupGraphPatternSub ) '}' 
GroupGraphPattern_p << Group(LCURL_p + (SubSelect_p | GroupGraphPatternSub_p)('pattern') + RCURL_p)

# [52]    TriplesTemplate   ::=   TriplesSameSubject ( '.' TriplesTemplate? )? 
TriplesTemplate_p = Group(separatedList(TriplesSameSubject_p, sep='.') + Optional(PERIOD_p)).setName('TriplesTemplate')
sparqlparser.addElement(TriplesTemplate_p)

# [51]    QuadsNotTriples   ::=   'GRAPH' VarOrIri '{' TriplesTemplate? '}' 
QuadsNotTriples_p = Group(GRAPH_p + VarOrIri_p + LCURL_p + Optional(TriplesTemplate_p) + RCURL_p ).setName('QuadsNotTriples')
sparqlparser.addElement(QuadsNotTriples_p)

# [50]    Quads     ::=   TriplesTemplate? ( QuadsNotTriples '.'? TriplesTemplate? )* 
Quads_p = Group(Optional(TriplesTemplate_p) + ZeroOrMore(QuadsNotTriples_p + Optional(PERIOD_p) + Optional(TriplesTemplate_p)) ).setName('Quads')
sparqlparser.addElement(Quads_p)

# [49]    QuadData          ::=   '{' Quads '}' 
QuadData_p = Group(LCURL_p + Quads_p + RCURL_p ).setName('QuadData')
sparqlparser.addElement(QuadData_p)

# [48]    QuadPattern       ::=   '{' Quads '}' 
QuadPattern_p = Group(LCURL_p + Quads_p + RCURL_p ).setName('QuadPattern')
sparqlparser.addElement(QuadPattern_p)

# [46]    GraphRef          ::=   'GRAPH' iri 
GraphRef_p = Group(GRAPH_p + iri_p ).setName('GraphRef')
sparqlparser.addElement(GraphRef_p)

# [47]    GraphRefAll       ::=   GraphRef | 'DEFAULT' | 'NAMED' | 'ALL' 
GraphRefAll_p = Group(GraphRef_p | DEFAULT_p | NAMED_p | ALL_p ).setName('GraphRefAll')
sparqlparser.addElement(GraphRefAll_p)

# [45]    GraphOrDefault    ::=   'DEFAULT' | 'GRAPH'? iri 
GraphOrDefault_p = Group(DEFAULT_p | (Optional(GRAPH_p) + iri_p) ).setName('GraphOrDefault')
sparqlparser.addElement(GraphOrDefault_p)

# [44]    UsingClause       ::=   'USING' ( iri | 'NAMED' iri ) 
UsingClause_p = Group(USING_p + (iri_p | (NAMED_p + iri_p)) ).setName('UsingClause')
sparqlparser.addElement(UsingClause_p)

# [43]    InsertClause      ::=   'INSERT' QuadPattern 
InsertClause_p = Group(INSERT_p + QuadPattern_p ).setName('InsertClause')
sparqlparser.addElement(InsertClause_p)

# [42]    DeleteClause      ::=   'DELETE' QuadPattern 
DeleteClause_p = Group(DELETE_p + QuadPattern_p ).setName('DeleteClause')
sparqlparser.addElement(DeleteClause_p)

# [41]    Modify    ::=   ( 'WITH' iri )? ( DeleteClause InsertClause? | InsertClause ) UsingClause* 'WHERE' GroupGraphPattern 
Modify_p = Group(Optional(WITH_p + iri_p) + ( (DeleteClause_p + Optional(InsertClause_p) ) | InsertClause_p ) + ZeroOrMore(UsingClause_p) + WHERE_p + GroupGraphPattern_p ).setName('Modify')
sparqlparser.addElement(Modify_p)

# [40]    DeleteWhere       ::=   'DELETE WHERE' QuadPattern 
DeleteWhere_p = Group(DELETE_WHERE_p + QuadPattern_p ).setName('DeleteWhere')
sparqlparser.addElement(DeleteWhere_p)

# [39]    DeleteData        ::=   'DELETE DATA' QuadData 
DeleteData_p = Group(DELETE_DATA_p + QuadData_p ).setName('DeleteData')
sparqlparser.addElement(DeleteData_p)

# [38]    InsertData        ::=   'INSERT DATA' QuadData 
InsertData_p = Group(INSERT_DATA_p + QuadData_p ).setName('InsertData')
sparqlparser.addElement(InsertData_p)

# [37]    Copy      ::=   'COPY' 'SILENT'? GraphOrDefault 'TO' GraphOrDefault 
Copy_p = Group(COPY_p + Optional(SILENT_p) + GraphOrDefault_p + TO_p + GraphOrDefault_p ).setName('Copy')
sparqlparser.addElement(Copy_p)

# [36]    Move      ::=   'MOVE' 'SILENT'? GraphOrDefault 'TO' GraphOrDefault 
Move_p = Group(MOVE_p + Optional(SILENT_p) + GraphOrDefault_p + TO_p + GraphOrDefault_p ).setName('Move')
sparqlparser.addElement(Move_p)

# [35]    Add       ::=   'ADD' 'SILENT'? GraphOrDefault 'TO' GraphOrDefault 
Add_p = Group(ADD_p + Optional(SILENT_p) + GraphOrDefault_p + TO_p + GraphOrDefault_p ).setName('Add')
sparqlparser.addElement(Add_p)

# [34]    Create    ::=   'CREATE' 'SILENT'? GraphRef 
Create_p = Group(CREATE_p + Optional(SILENT_p) + GraphRef_p).setName('Create')
sparqlparser.addElement(Create_p)

# [33]    Drop      ::=   'DROP' 'SILENT'? GraphRefAll 
Drop_p = Group(DROP_p + Optional(SILENT_p) + GraphRefAll_p).setName('Drop')
sparqlparser.addElement(Drop_p)

# [32]    Clear     ::=   'CLEAR' 'SILENT'? GraphRefAll 
Clear_p = Group(CLEAR_p + Optional(SILENT_p) + GraphRefAll_p ).setName('Clear')
sparqlparser.addElement(Clear_p)

# [31]    Load      ::=   'LOAD' 'SILENT'? iri ( 'INTO' GraphRef )? 
Load_p = Group(LOAD_p + Optional(SILENT_p) + iri_p  + Optional(INTO_p + GraphRef_p)).setName('Load')
sparqlparser.addElement(Load_p)

# [30]    Update1   ::=   Load | Clear | Drop | Add | Move | Copy | Create | InsertData | DeleteData | DeleteWhere | Modify 
Update1_p = Group(Load_p | Clear_p | Drop_p | Add_p | Move_p | Copy_p | Create_p | InsertData_p | DeleteData_p | DeleteWhere_p | Modify_p ).setName('Update1')
sparqlparser.addElement(Update1_p)

Prologue_p = Forward().setName('Prologue')
sparqlparser.addElement(Prologue_p)

Update_p = Forward().setName('Update')
sparqlparser.addElement(Update_p)

# [29]    Update    ::=   Prologue ( Update1 ( ';' Update )? )? 
Update_p << Group(Prologue_p + Optional(Update1_p + Optional(SEMICOL_p + Update_p)))

# [28]    ValuesClause      ::=   ( 'VALUES' DataBlock )? 
ValuesClause_p = Group(Optional(VALUES_p + DataBlock_p) ).setName('ValuesClause')
sparqlparser.addElement(ValuesClause_p)

# [27]    OffsetClause      ::=   'OFFSET' INTEGER 
OffsetClause_p = Group(OFFSET_p + INTEGER_p ).setName('OffsetClause')
sparqlparser.addElement(OffsetClause_p)

# [26]    LimitClause       ::=   'LIMIT' INTEGER 
LimitClause_p = Group(LIMIT_p + INTEGER_p ).setName('LimitClause')
sparqlparser.addElement(LimitClause_p)

# [25]    LimitOffsetClauses        ::=   LimitClause OffsetClause? | OffsetClause LimitClause? 
LimitOffsetClauses_p = Group((LimitClause_p + Optional(OffsetClause_p)) | (OffsetClause_p + Optional(LimitClause_p))).setName('LimitOffsetClauses')
sparqlparser.addElement(LimitOffsetClauses_p)

# [24]    OrderCondition    ::=   ( ( 'ASC' | 'DESC' ) BrackettedExpression ) | ( Constraint | Var ) 
OrderCondition_p =   Group(((ASC_p | DESC_p) + BracketedExpression_p) | (Constraint_p | Var_p)).setName('OrderCondition')
sparqlparser.addElement(OrderCondition_p)

# [23]    OrderClause       ::=   'ORDER' 'BY' OrderCondition+ 
OrderClause_p = Group(ORDER_BY_p + OneOrMore(OrderCondition_p) ).setName('OrderClause')
sparqlparser.addElement(OrderClause_p)

# [22]    HavingCondition   ::=   Constraint 
HavingCondition_p = Group(Constraint_p).setName('HavingCondition')
sparqlparser.addElement(HavingCondition_p)

# [21]    HavingClause      ::=   'HAVING' HavingCondition+ 
HavingClause_p = Group(HAVING_p + OneOrMore(HavingCondition_p) ).setName('HavingClause')
sparqlparser.addElement(HavingClause_p)

# [20]    GroupCondition    ::=   BuiltInCall | FunctionCall | '(' Expression ( 'AS' Var )? ')' | Var 
GroupCondition_p = Group(BuiltInCall_p | FunctionCall_p | (LPAR_p + Expression_p + Optional(AS_p + Var_p) + RPAR_p) | Var_p ).setName('GroupCondition')
sparqlparser.addElement(GroupCondition_p)

# [19]    GroupClause       ::=   'GROUP' 'BY' GroupCondition+ 
GroupClause_p = Group(GROUP_BY_p + OneOrMore(GroupCondition_p) ).setName('GroupClause')
sparqlparser.addElement(GroupClause_p)

# [18]    SolutionModifier          ::=   GroupClause? HavingClause? OrderClause? LimitOffsetClauses? 
SolutionModifier_p = Group(Optional(GroupClause_p) + Optional(HavingClause_p) + Optional(OrderClause_p) + Optional(LimitOffsetClauses_p) ).setName('SolutionModifier')
sparqlparser.addElement(SolutionModifier_p)

# [17]    WhereClause       ::=   'WHERE'? GroupGraphPattern 
WhereClause_p = Group(Optional(WHERE_p) + GroupGraphPattern_p ).setName('WhereClause')
sparqlparser.addElement(WhereClause_p)

# [16]    SourceSelector    ::=   iri 
SourceSelector_p = Group(iri_p).setName('SourceSelector')
sparqlparser.addElement(SourceSelector_p)

# [15]    NamedGraphClause          ::=   'NAMED' SourceSelector 
NamedGraphClause_p = Group(NAMED_p + SourceSelector_p ).setName('NamedGraphClause')
sparqlparser.addElement(NamedGraphClause_p)

# [14]    DefaultGraphClause        ::=   SourceSelector 
DefaultGraphClause_p = Group(SourceSelector_p).setName('DefaultGraphClause')
sparqlparser.addElement(DefaultGraphClause_p)

# [13]    DatasetClause     ::=   'FROM' ( DefaultGraphClause | NamedGraphClause ) 
DatasetClause_p = Group(FROM_p + (DefaultGraphClause_p | NamedGraphClause_p) ).setName('DatasetClause')
sparqlparser.addElement(DatasetClause_p)

# [12]    AskQuery          ::=   'ASK' DatasetClause* WhereClause SolutionModifier 
AskQuery_p = Group(ASK_p + ZeroOrMore(DatasetClause_p) + WhereClause_p + SolutionModifier_p ).setName('AskQuery')
sparqlparser.addElement(AskQuery_p)

# [11]    DescribeQuery     ::=   'DESCRIBE' ( VarOrIri+ | '*' ) DatasetClause* WhereClause? SolutionModifier 
DescribeQuery_p = Group(DESCRIBE_p + (OneOrMore(VarOrIri_p) | ALL_VALUES_p) + ZeroOrMore(DatasetClause_p) + Optional(WhereClause_p) + SolutionModifier_p ).setName('DescribeQuery')
sparqlparser.addElement(DescribeQuery_p)

# [10]    ConstructQuery    ::=   'CONSTRUCT' ( ConstructTemplate DatasetClause* WhereClause SolutionModifier | DatasetClause* 'WHERE' '{' TriplesTemplate? '}' SolutionModifier ) 
ConstructQuery_p = Group(CONSTRUCT_p + ((ConstructTemplate_p + ZeroOrMore(DatasetClause_p) + WhereClause_p + SolutionModifier_p) | \
                                      (ZeroOrMore(DatasetClause_p) + WHERE_p + LCURL_p +  Optional(TriplesTemplate_p) + RCURL_p + SolutionModifier_p))).setName('ConstructQuery')
sparqlparser.addElement(ConstructQuery_p)

# [9]     SelectClause      ::=   'SELECT' ( 'DISTINCT' | 'REDUCED' )? ( ( Var | ( '(' Expression 'AS' Var ')' ) )+ | '*' ) 
SelectClause_p = Group(SELECT_p + Optional(DISTINCT_p | REDUCED_p) + ( OneOrMore(Var_p | (LPAR_p + Expression_p + AS_p + Var_p + RPAR_p)) | ALL_VALUES_p ) ).setName('SelectClause')
sparqlparser.addElement(SelectClause_p)

# [8]     SubSelect         ::=   SelectClause WhereClause SolutionModifier ValuesClause 
SubSelect_p << Group(SelectClause_p + WhereClause_p + SolutionModifier_p + ValuesClause_p)

# [7]     SelectQuery       ::=   SelectClause DatasetClause* WhereClause SolutionModifier 
SelectQuery_p = Group(SelectClause_p + ZeroOrMore(DatasetClause_p) + WhereClause_p + SolutionModifier_p ).setName('SelectQuery')
sparqlparser.addElement(SelectQuery_p)

# [6]     PrefixDecl        ::=   'PREFIX' PNAME_NS IRIREF 
PrefixDecl_p = Group(PREFIX_p + PNAME_NS_p + IRIREF_p ).setName('PrefixDecl')
sparqlparser.addElement(PrefixDecl_p)

# [5]     BaseDecl          ::=   'BASE' IRIREF 
BaseDecl_p = Group(BASE_p + IRIREF_p ).setName('BaseDecl')
sparqlparser.addElement(BaseDecl_p)

# [4]     Prologue          ::=   ( BaseDecl | PrefixDecl )* 
Prologue_p << Group(ZeroOrMore(BaseDecl_p | PrefixDecl_p))

# [3]     UpdateUnit        ::=   Update 
UpdateUnit_p = Group(Update_p ).setName('UpdateUnit')
sparqlparser.addElement(UpdateUnit_p)

# [2]     Query     ::=   Prologue ( SelectQuery | ConstructQuery | DescribeQuery | AskQuery ) ValuesClause 
Query_p = Group(Prologue_p + ( SelectQuery_p | ConstructQuery_p | DescribeQuery_p | AskQuery_p ) + ValuesClause_p ).setName('Query')
sparqlparser.addElement(Query_p)

# [1]     QueryUnit         ::=   Query 
QueryUnit_p = Group(Query_p).setName('QueryUnit')
sparqlparser.addElement(QueryUnit_p)
 
if __name__ == '__main__':
    s = '"work"@en-bf'
    r = RDFLiteral_p.parseString(s)[0]
    print(r.dump())
    r = sparqlparser.RDFLiteral(s)
    print(r.dump())
    pass

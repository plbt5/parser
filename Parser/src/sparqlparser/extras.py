'''
Created on 29 mrt. 2016

@author: jeroenbruijning
'''
from pyparsing import delimitedList
from sparqlparser import do_parseactions
from sparqlparser.base import ParseInfo

def separatedList(pattern, sep=','):
    '''Similar to a delimited list of instances from a ParseInfo subclass, but includes the separator in its ParseResults. Returns a 
    ParseResults object containing a simple list of matched tokens separated by the separator.'''
      
    def makeList(parseresults):
        assert len(parseresults) > 0, 'internal error'
        assert len(list((parseresults.keys()))) <= 1, 'internal error, got more than one key: {}'.format(list(parseresults.keys()))
        label = list(parseresults.keys())[0] if len(list(parseresults.keys())) == 1 else None
        assert all([p.__class__.pattern == pattern for p in parseresults if isinstance(p, ParseInfo)]), 'internal error: pattern mismatch ({}, {})'.format(p.__class__.pattern, pattern)
        templist = []
        for item in parseresults:
            if isinstance(item, ParseInfo):
                i = [label, item]
                item.__dict__['label'] = i[0]
                templist.append([label, item])
            else:
                assert isinstance(item, str)
                templist.append([None, item])
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
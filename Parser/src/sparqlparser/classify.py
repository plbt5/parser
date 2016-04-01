'''
Created on 4 mrt. 2016

@author: jeroenbruijning
'''

from sparqlparser.grammar import *
from sparqlparser.rules import *

class Operators:
    pass

class Keywords:
    pass

class Terminals:
    pass

class NonTerminals:
    VarOrIri = Group(Var_p | iri_p).setName('VarOrIri')
    

    
def makeParser(operatorClass, keywordClass, terminalClass, nonterminalClass):
     
    def classify(wrappedPattern, token_class):
        result = type(wrappedPattern[0].name, (token_class,), {'pattern': wrappedPattern[0]})
        wrappedPattern[0].setParseAction(parseInfoFunc(result))
        return result     
             
    class _parser: pass
     
    sparqlparser = _parser()
     
    operatorNames = [o for o in operatorClass.__dict__ if not o.startswith('__')]
    keywordNames = [o for o in keywordClass.__dict__ if not o.startswith('__')]
    terminalNames = [o for o in terminalClass.__dict__ if not o.startswith('__')]
    nonterminalNames = [o for o in nonterminalClass.__dict__ if not o.startswith('__')]
     
    for o in operatorNames:
        pass
    for o in keywordNames:
        pass
    for o in terminalNames:
        pass
    for o in nonterminalNames:
        setattr(sparqlparser, o, classify([nonterminalClass.__dict__[o]], NonTerminal_))
         
    return sparqlparser
        
print('making sparqlparser')
sparqlparser = makeParser(Operators, Keywords, Terminals, NonTerminals)
print()

# VarOrIri_p = Group(Var_p | iri_p).setName('VarOrIri')
# class VarOrIri(NonTerminal_): pass
# if do_parseactions: VarOrIri_p.setName('VarOrIri').setParseAction(parseInfoFunc((VarOrIri)))


 
new_class = sparqlparser.VarOrIri
  
l = '$algebra', '<test>', 'az:Xy'
  
for s in l:    
    r1 = new_class(s)
    print(r1.dump())
    print('en nu parseString:\n')
    r2 = VarOrIri(s)
    print(r2.dump())

    assert r1.items == r2.items
    print(type(r1), type(r2))
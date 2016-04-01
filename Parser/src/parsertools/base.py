'''
Created on 3 mrt. 2016

@author: jeroenbruijning
'''
from pyparsing import *
from parsertools import SparqlParserException

class ParseInfo:
    '''Parent class for all ParseInfo subclasses. These subclasses correspond to productions in the SPARQL EBNF grammar.'''
    def __init__(self, *args):
        '''A ParseInfo object can be initialized wih either a valid string for the subclass concerned,
        using its own pattern attribute to parse it, or it can be initialized with a label and a list of items
        which together form an existing and valid parse result. The latter option is only meant to be
        used by internal parser processes. The normal use case is to feed it with a string.
        Each of the items is a pair consisting of a label and either
        - a string
        - another ParseInfo object.
        Only in the latter case the label can be other than None.
        This nested list is the basic internal structure for the class and contains all parsing information.'''
        
#         print('ParseInfo in   :', args)
        self.__dict__['label'] = None
        self.__dict__['parent'] = None
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
        '''Compares the items part of both instances (of the same class) for equality, recursively.
        This means that the labels  and parent pointers are not taken into account. This is because
        these are a form of annotation, separate from the parse tree in terms of
        encountered production rules. Equality means that all productions are identical.'''
        return self.__class__ == other.__class__ and self.items == other.items
    
    def __getattr__(self, att):
        '''Retrieves the attribute concerned, if it exists. Otherwise, it returns the unique element corresponding to the label (non-recursive) if that exists.
        Raises an exception if zero, or more than one values exist for that label.'''
        if att in self.__dict__:
            return self.__dict__[att]
        if att in self.getLabels():
            values = self.getValuesForLabel(att)
            assert len(values) == 1, values
            return values[0] 
        else:
            raise AttributeError('No attribute, or unique label found.')
#         
    def __setattr__(self, label, value):
        '''Raises exception when trying to set attributes directly.Elements are to be changed using "updateWith()".'''
        raise AttributeError('Direct setting of attributes not allowed. To change a labeled element, try updateWith() instead.')
    
    def __repr__(self):
        return self.__class__.__name__ + '("' + str(self) + '")'
    
    def __str__(self):
        '''Generates the string corresponding to the object. Except for whitespace variations, 
        this is identical to the string that was used to create the object.'''
        sep = ' '
        result = []
        for t in self.items:
            if isinstance(t, str):
                result.append(t) 
            else:
                if not isinstance(t, ParseInfo):
                    print()
                assert isinstance(t, ParseInfo), '__str__: found value {} of type {} instead of ParseInfo instance'.format(t, type(t))
                result.append(str(t))
        return sep.join([r for r in result if r != ''])
   
#     def __isLabelConsistent(self):
#         '''Checks if for labels are only not None for pairs [label, value] where value is a ParseInfo instance, and in those cases label must be equal to value.name.
#         This is for internal use only.'''
#         return all([i[0] == i[1].label if isinstance(i[1], ParseInfo) else i[0] == None if isinstance(i[1], str) else False for i in self.getItems()]) and \
#                 all([i[1].__isLabelConsistent() if isinstance(i[1], ParseInfo) else i[0] == None for i in self.getItems()])

    def __getPattern(self):
        '''Returns the pattern used to parse expressions for this class.'''
        return self.__class__.pattern
    
    def copy(self):
        '''Returns a deep copy of itself.'''
        result = self.pattern.parseString(str(self))[0]
        assert result == self
        return result
    
    def __getElements(self, labeledOnly = True):
        '''For internal use. Returns a flat list of all enmbedded ParseInfo instances (inclusing itself),
        at any depth of recursion.
        If labeledOnly is True, then in addition label may not be None.'''
        
        def flattenElement(p):
            result = []
            if isinstance(p, ParseInfo):
                result.extend(p.__getElements(labeledOnly=labeledOnly))
#             elif isinstance (p[1], list):
#                 result.extend(flattenList(p[1]))
            else:
                assert isinstance(p, str), type(p)
            return result
        
        def flattenList(l):
            result = []
            for p in l:
                result.extend(flattenElement(p))
            return result
        
        result = []
        if self.getLabel() or not labeledOnly:
                result.append(self)
        result.extend(flattenList(self.getItems()))
        return result  
    
    def createParentPointers(self):
        for i in self.getItems():
            if isinstance(i, ParseInfo):
                i.__dict__['parent'] = self
    
    def searchElements(self, *, label=None, element_type = None, value = None, labeledOnly=False):
        '''Returns a list of all elements with the specified search pattern. If labeledOnly is True,
        only elements with label not None are considered for inclusion. Otherwise (the default case) all elements are considered.
        Keyword arguments label, element_type, value are used as a wildcard if None. All must be matched for an element to be included in the result.'''
        
        result = []
        
        for e in [self] + self.__getElements(labeledOnly=labeledOnly):
#             print('DEBUG: e.name =', e.getLabel())

            if labeledOnly and not e.getLabel():
                continue
            if label and label != e.getLabel():
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
        return self.yieldsValidExpression() and self.isValid()

    def getLabel(self):
        '''Returns name attribute (non-recursive).'''
        return self.label

    def getItems(self):
        '''Returns items attribute (non-recursive).'''
        return self.items
    
    def getValues(self):
        '''Returns list of all values from items attribute (non-recursive).'''
        return [i[1] for i in self.getItems()]
     
    def getLabels(self):
        '''Returns list of all labels from items attribute (non-recursive).'''
        return(filter(None, [i.getLabel() for i in self.getItems() if isinstance(i, ParseInfo)]))
    
    def hasLabel(self, k):
        '''True if k present as label (non-recursive).'''
        return k in self.getLabels()
    
    def getValuesForLabel(self, k):
        '''Returns list of all values for label. (Non-recursive).'''
        return [i for i in self.getItems() if isinstance(i, ParseInfo) and i.label == k]
    
#     def getItemsForLabel(self, k):
#         '''Returns list of items with given label. (Non-recursive).'''
#         return [i for i in self.getItems() if isinstance(i, ParseInfo) and i.label == k]
    
    def getChildren(self):
        '''Returns a list of all its child elements.'''
        return [i for i in self.getItems() if isinstance(i, ParseInfo)]
    
    def getParent(self):
        '''Returns a list of its parent element, which is the first element encountered when going up in the parse tree.
        For the top element, the method returns None'''
        return self.parent
    
    def getAncestors(self):
        '''Returns the list of parent nodes, starting with the direct parent and ending with the top element.'''
        result = []
        parent = self.getParent()
        while parent:
            result.append(parent)
            parent = parent.getParent()
        return result
    
    def isBranch(self):
        '''Checks whether the node branches.'''
        return len(self.getItems()) > 1
            
    def isAtom(self):
        '''Test whether the node has no ParseInfo subnode, but instead contains a string.'''
        return len(self.getItems()) == 1 and isinstance(self.items[0], str)
    
    def descend(self):
        '''Descends until either an atom or a branch node is encountered; returns that node.'''
        result = self
        while not result.isAtom() and not result.isBranch():
            result = result.items[0]
        return result
        
    def dump(self, indent='', step='|  '):
        '''Returns a dump of the object, with rich information'''
        result = ''
        def dumpString(s, indent, step):
            return indent + s + '\n'
        
        def dumpItems(items, indent, step):
            result = ''
            for i in items:
                if isinstance(i, str):
                    result += dumpString(i, indent+step, step)
#                 elif isinstance(v, list):
#                     dumpItems(v, indent+step, step)
                else:
                    assert isinstance(i, ParseInfo) 
                    result += i.dump(indent+step, step)
            return result       
       
        result += indent + ('> '+ self.getLabel() + ':\n' + indent if self.getLabel() else '') + '[' + self.__class__.__name__ + '] ' + '/' + self.__str__() + '/' + '\n'
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
    '''Returns the function that converts a ParseResults object to a ParseInfo object of class "cls", with label set to None, and
    items set to a recursive list of [None, value] pairs (see below).
    The function returned is used to set a parseAction for a pattern.'''
            
    def labeledList(parseresults):
        '''For internal use. Converts a ParseResults object to a recursive structure consisting of a list of pairs [None, obj],
        obj either a string, a ParseInfo object, or again a similar list.'''
#         print(cls)
#         print('LabeledList in :', parseresults)
        while len(parseresults) == 1 and isinstance(parseresults[0], ParseResults):
            parseresults = parseresults[0]
        valuedict = dict((id(t), k) for (k, t) in parseresults.items())
        assert len(valuedict) == len(list(parseresults.items())), 'internal error: len(valuedict) = {}, len(parseresults.items) = {}'.format(len(valuedict), len(list(parseresults.items)))
        result = []
        for t in parseresults:
            if isinstance(t, str):
#                 i = [None, t]
#                 result.append(i)
                result.append(t)
            elif isinstance(t, ParseInfo):
#                 t.createParentPointers()
#                 i = [valuedict.get(id(t)), t]
#                 t.__dict__['label'] = i[0]
#                 result.append(i)
                if t.__dict__['label'] == None:
                    t.__dict__['label'] = valuedict.get(id(t))
                result.append(t)
            elif isinstance(t, list):
                result.append(t)
            else:
                assert isinstance(t, ParseResults), type(t)
#                 if not valuedict.get(id(t)) == None:
#                     print()
#                 if valuedict.get(id(t)) != None:
#                     print('\n*** label {} found for compound expression {}'.format(valuedict.get(id(t)), t.__str__()))
                assert valuedict.get(id(t)) == None, 'Error: found label ({}) for compound expression {}, remove'.format(valuedict.get(id(t)), t.__str__())
                result.extend(labeledList(t))
#         print('LabeledList uit:', result)
        return result
    
    def makeparseinfo(parseresults):
        '''The function to be returned.'''
        assert ParseInfo in cls.__bases__
        assert isinstance(parseresults, ParseResults)
        return cls(None, labeledList(parseresults))  
    
    return makeparseinfo

class Parser:
    def addElement(self, pattern):
        setattr(self, pattern.name, type(pattern.name, (ParseInfo,), {'pattern': pattern}))
        pattern.setParseAction(parseInfoFunc(getattr(self, pattern.name)))
                           

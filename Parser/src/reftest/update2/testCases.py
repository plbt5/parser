'''
Created on 23 feb. 2016

@author: jeroenbruijning
'''
from sparqlparser.grammar import *

actions = {'mf:PositiveUpdateSyntaxTest11': [], 'mf:NegativeUpdateSyntaxTest11': []}

lines = [l.split() for l in open('manifest.ttl') if ('mf:PositiveUpdateSyntaxTest11' in l or 'mf:NegativeUpdateSyntaxTest11' in l or 'mf:action' in l) and not l.startswith('#')]

for i in range(len(lines)//2):
    actions[lines[2*i][1]].append(lines[2*i+1][1][1:-1])
 
posNum = len(actions['mf:PositiveUpdateSyntaxTest11'])
negNum = len(actions['mf:NegativeUpdateSyntaxTest11'])

print('Testing {} positive and {} negative testcases'.format(posNum, negNum))

for fname in actions['mf:PositiveUpdateSyntaxTest11']:
    try:
        s = stripComments(open(fname).readlines())
        r = UpdateUnit(s)
    except ParseException as e:
        print('\n*** {} should not raise exception? Check'.format(fname))

for fname in actions['mf:NegativeUpdateSyntaxTest11']:
    try:
        s = open(fname).read()
        r = UpdateUnit(s)
        print('\n*** {} should raise exception? Check'.format(fname))
    except ParseException as e:
        pass
print('\nPassed')
    


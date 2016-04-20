'''
Created on 11 mrt. 2016

@author: jeroenbruijning
'''

from subprocess import *
import parsertools
import os

os.chdir('reftest/fed')
print('Running fed test/n')
print(check_output(['/Library/Frameworks/Python.framework/Versions/3.5/bin/python3.5', 'testCases.py']).decode('utf-8'))
os.chdir('../query')
print('\nRunning query test\n')
print(check_output(['/Library/Frameworks/Python.framework/Versions/3.5/bin/python3.5', 'testCases.py']).decode('utf-8'))
os.chdir('../update1')
print('\nRunning update1 test\n')
print(check_output(['/Library/Frameworks/Python.framework/Versions/3.5/bin/python3.5', 'testCases.py']).decode('utf-8'))
os.chdir('../query')
print('\nRunning update2 test\n')
print(check_output(['/Library/Frameworks/Python.framework/Versions/3.5/bin/python3.5', 'testCases.py']).decode('utf-8'))
os.chdir('../..')
print('\nRunning func_test test\n')
print(check_output(['/Library/Frameworks/Python.framework/Versions/3.5/bin/python3.5', 'grammar_functest.py']).decode('utf-8'))
print('\nRunning func_unittest test\n')
print(check_output(['/Library/Frameworks/Python.framework/Versions/3.5/bin/python3.5', 'func_unittest.py']).decode('utf-8'))
print('\nRunning grammar_unittest test\n')
print(check_output(['/Library/Frameworks/Python.framework/Versions/3.5/bin/python3.5', 'grammar_unittest.py']).decode('utf-8'))
print('\nAll tests finished')
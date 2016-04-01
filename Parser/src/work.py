lines = list(open('parsertools/parser.py'))

print(len([l for l in lines if l.startswith('parsertools.addElement')]))
lines = list(open('sparqlparser/parser.py'))

print(len([l for l in lines if l.startswith('sparqlparser.addElement')]))
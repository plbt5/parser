'''
Created on 13 apr. 2016

@author: jeroenbruijning
'''

# Test cases taken from https://tools.ietf.org/html/rfc3986#section-5.4

import rfc3987

base = 'http://a/b/c/d;p?q'

testcases = [
            ["g:h", "g:h"],
            ["g", "http://a/b/c/g"],
            ["./g", "http://a/b/c/g"],
            ["g/", "http://a/b/c/g/"],
            ["/g", "http://a/g"],
            ["//g", "http://g"],
            ["?y", "http://a/b/c/d;p?y"],
            ["g?y", "http://a/b/c/g?y"],
            ["#s", "http://a/b/c/d;p?q#s"],
            ["g#s", "http://a/b/c/g#s"],
            ["g?y#s", "http://a/b/c/g?y#s"],
            [";x", "http://a/b/c/;x"],
            ["g;x", "http://a/b/c/g;x"],
            ["g;x?y#s", "http://a/b/c/g;x?y#s"],
            ["", "http://a/b/c/d;p?q"],
            [".", "http://a/b/c/"],
            ["./", "http://a/b/c/"],
            ["..", "http://a/b/"],
            ["../", "http://a/b/"],
            ["../g", "http://a/b/g"],
            ["../..", "http://a/"],
            ["../../", "http://a/"],
            ["../../g", "http://a/g"],
            ["../../../g", "http://a/g"],
            ["../../../../g", "http://a/g"],
            ["/./g", "http://a/g"],
            ["/../g", "http://a/g"],
            ["g.", "http://a/b/c/g."],
            [".g", "http://a/b/c/.g"],
            ["g..", "http://a/b/c/g.."],
            ["..g", "http://a/b/c/..g"],
            ["./../g", "http://a/b/g"],
            ["./g/.", "http://a/b/c/g/"],
            ["g/./h", "http://a/b/c/g/h"],
            ["g/../h", "http://a/b/c/h"],
            ["g;x=1/./y", "http://a/b/c/g;x=1/y"],
            ["g;x=1/../y", "http://a/b/c/y"],
            ["g?y/./x", "http://a/b/c/g?y/./x"],
            ["g?y/../x", "http://a/b/c/g?y/../x"],
            ["g#s/./x", "http://a/b/c/g#s/./x"],
            ["g#s/../x", "http://a/b/c/g#s/../x"],
            ["http:g", "http:g"]
            ]

for relative, resolved in testcases:
    assert rfc3987.resolve(base, relative) == resolved

print('Passed')

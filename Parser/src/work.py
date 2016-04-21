def u2int(s):
    return int(s.replace('uU', 'x'))

# s = r'\\u12CA'
# 
# t = s.replace(r'\\u', r'x')
# print(t)
# print(int(t))

def escToUcode(s):
    assert (s[:2] == r'\u' and len(s) == 6) or (s[:2] == r'\U' and len(s) == 10)
    return chr(int(s[2:], 16))

print(escToUcode(r'\U000C00AA'))

import re



s = 'abra\\U000C00AAcada\\u00AAbr\u99DDa'



print(s)

def unescapeUcode(s):
    smallUcodePattern = r'\\u[0-9a-fA-F]{4}'
    largeUcodePattern = r'\\U[0-9a-fA-F]{8}'
    s = re.sub(smallUcodePattern, lambda x: escToUcode(x.group()), s)
    s = re.sub(largeUcodePattern, lambda x: escToUcode(x.group()), s)    
    return s

print(unescapeUcode(s))
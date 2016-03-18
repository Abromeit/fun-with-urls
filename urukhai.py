import random
import re

REGEX_GROUPS = ['[0-9]+', '[a-zA-Z]+', '[0-9a-zA-Z]+', '[0-9a-zA-Z._-]+', '/']

def get_regex(data, strings=True, depth=20):
    
    if not depth: 
        #sys.stderr.write(repr(data))
        return '.*'
    
    # Strip off common prefix
    prefix = ''
    if strings:
        ii = 0
        best = min(map(len, data))
        while ii < best:
            if not all(map(lambda x: x[ii] == data[0][ii], data)): 
                ii = ii if ii+1 < best else best
                break
            ii = ii+1
        if ii > 2:
            prefix = re.escape(data[0][:ii])
            data = map(lambda x: x[ii:], data)
    
    # Strip off common suffix
    suffix = ''
    if strings:
        ii = 0
        best = min(map(len, data))
        while ii > -best:
            ii = ii-1
            if not all(map(lambda x: x[ii] == data[0][ii], data)): 
                ii += 1
                break
        if ii < -1:
            suffix = re.escape(data[0][ii:])
            data = map(lambda x: x[:ii], data)
    
    # Check for empty remainder
    if not any(map(len, data)):
        return prefix + suffix
    
    # Look for regex that matches entire chunk 
    total_regex = None
    for regex in REGEX_GROUPS:
        if all(map(lambda x: type(re.match('^{}$'.format(regex), x)) != type(None), data)):
            total_regex = regex
    if total_regex:
        return prefix + total_regex + suffix

    # Find best regex that matches from front
    left_regex = ''
    candidates = {}
    for regex in REGEX_GROUPS:
        _regex = re.compile('^{}'.format(regex))
        if all(map(lambda x: type(_regex.match(x)) != type(None), data)):
            candidates[regex] = max(map(lambda x: len(_regex.sub('', x)), data))
    if len(candidates):
        left_regex = min(candidates.iteritems(), key=lambda x:x[1])[0]
        _regex = re.compile('^{}'.format(left_regex))
        data = map(lambda x: _regex.sub('', x), data)
        
    # Find best regex that matches from back
    right_regex = ''
    candidates = {}
    for regex in REGEX_GROUPS:
        _regex = re.compile('{}$'.format(regex))
        if all(map(lambda x: type(_regex.match(x)) != type(None), data)):
            candidates[regex] = max(map(lambda x: len(_regex.sub('', x)), data))
    if len(candidates):
        right_regex = min(candidates.iteritems(), key=lambda x:x[1])[0]
        _regex = re.compile('^{}'.format(right_regex))
        data = map(lambda x: _regex.sub('', x), data)
    
    # Check for optional parts
    optional_regex = ''
    if not len(left_regex + right_regex):
        optional = filter(len, data)
        if optional and len(optional) < len(data):
            optional_regex = get_regex(optional, False, depth-1)
            if optional_regex:
                optional_regex = '({})?'.format(optional_regex)
                _regex = re.compile(optional_regex)
                data = map(lambda x: _regex.sub('', x), data)
        
    
    # Recurse on remainder
    return prefix + left_regex + optional_regex + get_regex(data, strings, depth-1) + right_regex + suffix
    
def get_prefixes_random(data, select=3, rounds=25):
    matches = set()
    while len(matches) < rounds:
        regex = get_regex(random.sample(data, select))
        matches.add(regex)

    candidates = filter(lambda x: x.endswith('\/'), set(map(lambda x: x[:x.find('[')], matches)))
    prefixes = filter(lambda x: len(filter(lambda y: y.find(x) >= 0, candidates)) == 1, candidates)
    
    return map(lambda x: x.replace('\\', ''), prefixes)

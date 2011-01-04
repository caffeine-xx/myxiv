from lepl import *

def node(x):
    f = lambda y: {x:y}
    return f

def comp(*fs):
    def fn(val):
        return reduce(lambda x,y: y(x), fs[1:], fs[0](val))
    return fn

def test_comp():
    f1 = lambda x: x*2
    f2 = lambda x: x+3
    f3 = comp(f1,f2)
    x  = 3
    y  = (3*2)+3
    assert y == f3(x), "Expected %s, got %s" % tuple(map(str,(y, f3(x))))

class search_parser:
    keyword  = Word()                              >> node('keyword') 
    contains = SingleLineString(quote='"')         >> node('keyword')
    tag      = ~Literal('t:') & Word()             >> node('tag')
    year     = ~Literal('y:') & UnsignedInteger()  >> comp(int,node('year'))
    atom     = tag | year | contains | keyword 
    with DroppedSpace():
        expr = atom[:]

def parse(s):
    return search_parser.expr.parse(s)

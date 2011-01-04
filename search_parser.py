import datetime
from lepl import *


def node(x):
    f = lambda y: (x,y)
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
    """ Parser that builds queries """
    def __init__(self):
        pass
    def parse(self,s):
        return self.expr.parse(s)

class query_builder:
    """ Builds query dicts for mongoengine's Article collection 
        Allows chaining style like 
            x.tag("foo").year(1998)""" 
    def __init__(self):
        self.q = {}
    def exists(self,v):
        self.q.update({v:{'$exists':True}})
        return self
    def tag(self,v):
        return self.exists('tags__'+v)
    def keyword(self,v):
        return self.exists('description__ngram_prob__1__'+v)
    def year(self,v):
        k = 'published_on__gt'
        if not self.q.has_key(k) or (self.q.has_key(k) and v > self.q[k]):
            self.q['published_on__gt']=datetime.datetime(int(v),1,1)
        return self
    def get(self):
        return self.q

def parse(s):
    return search_parser().parse(s)

def parse_query(s):
    query = parse(s)
    qb = query_builder()
    for (k,v) in query:
        getattr(qb,k)(v)
    return qb.get()


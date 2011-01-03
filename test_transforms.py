import pymongo, nltk, time
from transforms import *
from nose import with_setup
import schema

def tval(i):
    return {'value': i,
            'const': 'const',
            'list': [i,i*2]}

def mongo_conn():
    return pymongo.Connection(host='localhost',port=27017)

def mongo_setup():
    conn = mongo_conn()
    conn.drop_database('testdb')
    conn.testdb.testcol.insert(map(tval,xrange(1000)))
    conn.disconnect()

@with_setup(mongo_setup)
def test_mongo_map():
    conn = mongo_conn()
    col = conn.testdb.testcol
    def fn(x):
        x['value'] = x['value'] * 2
        return x
    query = col.find({'value':{'$gt':500}})
    conn.testdb.drop_collection('maptest')
    maptest = conn.testdb.maptest
    ls_out, failed = mongo_map(fn, query, maptest, [])
    assert maptest.count()==query.count(), "All elements got transformed"
    assert failed == [], "No errors"
    for x in ls_out:
        assert int(x['value']) > 1000, "Transform happened"
    failed = mongo_map(fn, query, maptest, None)
    assert failed == [], "No errors when no listout"

    def fn2(x):
        if x['value']==600:
            raise Exception("bad")
        else:
            return fn(x)
    conn.testdb.drop_collection('maptest')
    query = col.find({'value':{'$gt':500}})
    failed = mongo_map(fn2, query, maptest, None)
    assert len(failed)==1, "Failed get returned properly"

def test_ensure_list():
    assert ensure_list('foo')==['foo'], "Wraps non-list"
    assert ensure_list(['foo'])==['foo'], "Doesn't wrap non-list"

def test_find_urls():
    data = ['abcde', 'scheme:abcde', 'http://abcde']
    assert find_urls(data)[0]=='http://abcde',"Found the url"
    assert find_urls(data[0:1])==[], 'No false urls'

def test_ymd_to_datetime():
    ymd = "2011-01-01"
    dt = ymd_to_datetime(ymd)
    assert dt.year == 2011, "Year"
    assert dt.month == 1, "Month"
    assert dt.day == 1, "Day"

def test_text_to_ngrams():
    txt = "a b a b c"
    out = text_to_ngrams(txt,2)
    fr1 = {'a': 2,   'b': 2,   'c': 1}
    pr1 = {'a': 0.4, 'b': 0.4, 'c': 0.2}
    fr2 = {'a b': 2,   'b a': 1,    'b c': 1}
    pr2 = {'a b': 0.5, 'b a': 0.25, 'b c': 0.25}

    print "Freq: ", out.ngram_freq

    assert out.ngram_freq["1"] == fr1, "Frequencies"
    assert out.ngram_freq["2"] == fr2, "Frequencies"
    assert out.ngram_prob["1"] == pr1, "Probability"
    assert out.ngram_prob["2"] == pr2, "Probability"
    assert out.words == txt.split(" "), "Words"

def test_arxiv_to_article():
    N=100
    min_hz = 20
    
    # copy N values from arxiv
    myxiv = mongo_conn().myxiv
    records = [x for x in myxiv.arxiv.find().limit(N)]
    
    testdb = schema.connect('testdb',host='127.0.0.1',port=27017)
    testdb.drop_collection("arxiv")
    testdb.drop_collection("article")
    testdb.arxiv.insert(records)
 
    # try to import them all as articles
    t0 = time.time()
    failed = mongo_map(lambda x: arxiv_to_article(x,True), testdb.arxiv.find())
    dt = time.time()-t0
    assert N/dt > min_hz, (N / dt, " rec/sec too slow, min is ", min_hz) 

    # Check they all made it
    assert failed==[], "No fails"
    assert testdb.article.count()==testdb.arxiv.count(), ("arxiv count ",testdb.arxiv.count(),", got article count ", testdb.article.count())


import search_parser, time, datetime
reload(search_parser)

def test_parse():
    kw = search_parser.node('keyword')
    yr = lambda x: search_parser.node('year')(int(x))
    tg = search_parser.node('tag')

    tests = {'foo':[kw('foo')],
             'foo bar':[kw('foo'),kw('bar')],
             'y:2000':[yr(2000)],
             't:tag':[tg('tag')],
             '"zig zag"':[kw("zig zag")]}
    # Ensure results are correct
    for s,r in tests.items():
        result = search_parser.parse(s)
        assert result==r, "Input %s, expected %s, got %s" % (s, str(r),str(result))
    t0 = time.time()
    N  = 20
    for x in xrange(N):
        map(search_parser.parse, tests.keys())
    dt = time.time()-t0
    print "Parses / sec: %0.2f" % (len(tests)*N/dt)

def test_query_builder():
    qb = search_parser.query_builder()
    ex = {"$exists":True}
    tests = [
        (lambda x: x.tag("tag1"),
            {"tags__tag1":ex}),
        (lambda x: x.tag("tag1").tag("tag2"),
            {"tags__tag1":ex,
             "tags__tag2":ex}),
        (lambda x:x.keyword("key1"),
            {'description__ngram_prob__1__key1':ex}),
        (lambda x:x.year("1998"),
            {"published_on__gt":datetime.datetime(1998,1,1)}),
        (lambda x:x.tag("tag1").tag("tag2").keyword('key1').keyword('key2').year('1998'),
            {"published_on__gt":datetime.datetime(1998,1,1),
             'description__ngram_prob__1__key1':ex,
             'description__ngram_prob__1__key2':ex,
             "tags__tag1":ex,
             "tags__tag2":ex})]
    for (f,v) in tests:
        q = f(search_parser.query_builder()).get()
        assert v==q, "Expected: %s, got %s" % (str(v),str(q))

def test_parse_query():
    qb = search_parser.query_builder()
    q1 = qb.tag("foo").keyword("bar").get()
    q2 = search_parser.parse_query("t:foo bar")
    assert q1==q2, "Expected: %s, got %s" % (str(v),str(q))

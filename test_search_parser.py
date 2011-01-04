import search_parser, time
reload(search_parser)

def test_parse():
    tests = {'foo':[{'keyword':'foo'}],
             'foo bar':[{'keyword':'foo'},{'keyword':'bar'}],
             'y:2000':[{'year':2000}],
             't:tag':[{'tag':'tag'}],
             '"zig zag"':[{'keyword':"zig zag"}]}
    # Ensure results are correct
    for s,r in tests.items():
        result = search_parser.parse(s)
        assert result==r, "Input %s, expected %s, got %s" % (s, str(r),str(result))
    t0 = time.time()
    N  = 10
    for x in xrange(N):
        map(search_parser.parse, tests.keys())
    dt = time.time()-t0
    print "Parses / sec: %0.2f" % (len(tests)*N/dt)


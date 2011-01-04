import webapp, datetime as dt
reload(webapp)

def test_parse_query():
    ex = {"$exists":True}
    tests = {
        "t:tag1":
            {"tags__tag1":ex},
        "t:tag1 t:tag2":
            {"tags__tag1":ex,
             "tags__tag2":ex},
        "k:key1":
            {"description__words":"key1"},
        "k:key1 k:key2":
            {"description__words__all":["key1","key2"]},
        "y:1998":
            {"published_on__gt":dt.datetime(1998,1,1)},
        "t:tag1 t:tag2 k:key1 k:key2 y:1998":
            {"published_on__gt":dt.datetime(1998,1,1),
             "description__words__all":["key1","key2"],
             "tags__tag1":ex,
             "tags__tag2":ex}}

    queries = tests.keys()
    results = tests.values()
    outputs = map(webapp.parse_query, queries)

    for query, result, parsed in zip(queries,results,outputs):
        assert parsed==result, "Query %s: should be %s, got %s" % (query, result, parsed)


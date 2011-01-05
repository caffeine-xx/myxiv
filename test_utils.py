import utils
reload(utils)

def test_ensure_list():
    assert utils.ensure_list('foo')==['foo'], "Wraps non-list"
    assert utils.ensure_list(['foo'])==['foo'], "Doesn't wrap non-list"

def test_merge():
    items = [('a','b'),('a','c'),('b','c')]
    result = {'a':['b','c'],'b':'c'}
    merged = utils.merge(items)
    assert result==merged, ("Required, got: ", result, merged)

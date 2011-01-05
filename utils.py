""" Some simple utilities """

def custom_merge(maps, on_key_match=lambda m,k,v:dict(m.items()+[(k,v)])):
    """ Merges together a list of maps
        When the currently merged set has a key
        overlapping the next map, calls 
            on_key_match(current, key, value)
        and uses the result as the new merged current """

    def merge_fn(m1,m2):
        for k,v in m2.items():
            if m1.has_key(k):
                m1 = on_key_match(m1,k,v)
            else:
                m1[k] = v
        return m1 

    return reduce(merge_fn, maps)

def list_key_match(m, k, v):
    if not isinstance(m[k],list):
        m[k] = [m[k],v]
    elif isinstance(m[k],list):
        m[k].append(v)
    return m

def merge(items, start=None):
    dicts = map(lambda i: dict([i]), items)
    if start: dicts.append(start)
    return custom_merge(dicts, list_key_match)

def ensure_list(a):
    if not isinstance(a,list):
        b = [a]
    else: b = a
    return b



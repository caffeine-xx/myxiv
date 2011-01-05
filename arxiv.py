import urllib2, time, os
from lxml import etree, objectify
from transforms import merge, arxiv_to_article
""" An arXiv client library """

arxiv_oai = "http://export.arxiv.org/oai2"

def ns_dc(s=""):
    return '{http://purl.org/dc/elements/1.1/}' + s
def ns_oai(s=""):
    return '{http://www.openarchives.org/OAI/2.0/}' + s
def ns_oai_dc(s=""):
    return '{http://www.openarchives.org/OAI/2.0/oai_dc/}' + s
def ns_path(expr):
    return objectify.ObjectPath(expr)

def children_to_list(elem, ns=""):
    ls = []
    for c in elem.iterchildren():
        ls.append((c.tag.replace(ns,""), c.text))
    return ls

def parse(readable):
    return objectify.parse(readable)

def run_query(url):
    """ Query a URL and run an XML parser on the result 
        Returns an lxml.objectify tree of the parsed result """
    query = urllib2.urlopen(url)
    tree = parse(query)
    return tree

### OAI ###

def oai_url(base_url, verb, prefix="oai_dc", range=None, token=None):
    """ Builds a URL for an OAI-PMH query
        base_url: url of the OAI service
        verb:  action to perform, one of ListIdentifiers, ListRecords
        range: date range: ['2010-01-01'] gives results from that date
                           ['2010-01-01','2010-01-07'] gives in the range
                           [None,'2010-01-07'] gives until 2010-01-07
        token: a resumption token (all other fields are ignored if this is not None) 
        prefix: metadataPrefix type (should usually be oai_dc) """
    query = ["verb="+verb]
    if token:
        query.append('resumptionToken='+token)
    else:
        if prefix:
            query.append('metadataPrefix='+prefix)
        if range and len(range)>0: 
            if range[0]:
                query.append('from='+range[0])
            if len(range)>1:
                query.append('until='+range[1])
    return base_url + "?" + "&".join(query)

def parse_inc(inc=None):
    if not isinstance(inc,int): 
        if inc is None: inc = 0
        else:           inc = int(inc)
    return inc

def oai_stream(base_url,verb,token=None,inc=None,prefix="oai_dc",range=None): 
    """ An iterator over a stream of result-sets, with waiting in between resumption tokens 
        Usage:
            for n, tree in iter_stream(..):
                # do stuff 
    """
    pause = 20.0
    url = oai_url(base_url, verb=verb, range=range, prefix="oai_dc")
    tree = None
    inc = parse_inc(inc)
    while True:
        if token:
            url = oai_url(oai.arxiv, verb=verb, token=token)
        try:
            print "Querying url " + url
            tree = run_query(url)
        except urllib2.HTTPError as err:
            if err.getcode() == 503: # rate limiting
                time.sleep(pause)
                continue
        yield inc, tree
        inc   = inc + 1
        token = resumption_token(tree)
        if token:
            print "Sleeping before resuming for " + str(pause)
            time.sleep(pause)
            continue
        else:
            print "Finished, no resumption token"
            break

def oai_resumption_token(tree):
    """ Finds a resumption token in a parsed xml tree """
    tokens = tree.xpath("//*[local-name()='resumptionToken']")
    if len(tokens) > 0: 
        return tokens[0]
    else:
        return None

def oai_identifiers(tree):
    """ Iterate over OAI-PMH headers """
    headers = path("OAI-PMH.ListIdentifiers.header").find(tree.getroot())
    for h in headers:
        yield merge(children_to_list(h, ns_oai()))

def oai_records(tree):
    """ Iterate over OAI-PMH records """
    records = ns_path("OAI-PMH.ListRecords.record").find(tree.getroot())
    for r in records:
        try:
            header = ns_path(".header").find(r)[0]
            meta   = ns_path(".metadata."+ns_oai_dc('dc')).find(r)[0]
            yield merge(children_to_list(header, ns_oai()) + children_to_list(meta, ns_dc()))
        except Exception as e:
            print e

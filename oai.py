import urllib2
from lxml import etree, objectify
from transforms import merge
""" An ultra-simple OAI-PMH client library
    Returns results as 
        - objectify trees
        - SON (e.g. maps and arrays) """

def dc(s=""):
    return '{http://purl.org/dc/elements/1.1/}' + s
def oai(s=""):
    return '{http://www.openarchives.org/OAI/2.0/}' + s
def oai_dc(s=""):
    return '{http://www.openarchives.org/OAI/2.0/oai_dc/}' + s
def path(expr):
    return objectify.ObjectPath(expr)

def children_to_list(elem, ns=""):
    ls = []
    for c in elem.iterchildren():
        ls.append((c.tag.replace(ns,""), c.text))
    return ls

def children_to_map(elem, ns=""):
    ls  = children_to_list(elem, ns)
    return merge(ls)         

def query_url(base_url, verb, prefix=None, range=None, token=None):
    """ Builds a URL for an OAI-PMH query
        base_url: url of the OAI service
        verb:  action to perform, one of ListIdentifiers, ListRecords
        range: date range: ['2010-01-01'] gives results from that date
                           ['2010-01-01','2010-01-07'] gives in the range
        token: a resumption token (all other fields are ignored if this is not None) 
        prefix: metadataPrefix type (should usually be oai_dc) """
    query = ["verb="+verb]
    if token:
        query.append('resumptionToken='+token)
    else:
        if prefix:
            query.append('metadataPrefix='+prefix)
        if range:
            query.append('from='+range[0])
            if len(range)>1:
                query.append('until='+range[1])
    return base_url + "?" + "&".join(query)

def run_query(url):
    query = urllib2.urlopen(url)
    tree = objectify.parse(query)
    return tree

def resumption_token(tree):
    tokens = tree.xpath("//*[local-name()='resumptionToken']")
    if len(tokens) > 0: 
        return tokens[0]
    else:
        return None

def iter_identifiers(tree):
    headers = path("OAI-PMH.ListIdentifiers.header").find(tree.getroot())
    for h in headers:
        yield children_to_map(h, oai())

def iter_records(tree):
    records = path("OAI-PMH.ListRecords.record").find(tree.getroot())
    for r in records:
        try:
            header = path(".header").find(r)[0]
            meta   = path(".metadata."+oai_dc('dc')).find(r)[0]
            yield merge(children_to_list(header, oai()) + children_to_list(meta, dc()))
        except Exception as e:
            print e

arxiv = "http://export.arxiv.org/oai2"

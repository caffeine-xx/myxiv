import nltk, re, time, datetime
from schema import *
from urllib2 import urlparse

def mongo_map(fn, query_in, coll_out=None, list_out=None):
    """ Maps a function over all documents from a query,
        puts results into an output collection and/or list"""
    failed = []
    for x in query_in:
        try:        
            y = fn(x)
            if coll_out:
                coll_out.insert(y)
            if list_out:
                list_out.append(y)
        except Exception as err:
            print "Fail: ", x, err
            failed.append((x,err))
    if list_out is not None:
        return list_out, failed
    else:
        return failed

def ensure_list(a):
    if not isinstance(a,list):
        b = [a]
    else: b = a
    return b

def find_urls(identifiers):
    urls = filter(lambda u: urlparse.urlparse(u).scheme=='http', 
                 identifiers)
    return urls

def text_to_ngrams(txt,max_n=3):
    out = Ngrams()
    out.fulltext = txt

    punct = re.compile("[^\w]")
    out.words = filter(lambda w: w != "", map(lambda w: punct.sub("",w), nltk.wordpunct_tokenize(txt)))

    out.sentences = nltk.sent_tokenize(txt)
    out.max_n = max_n
    out.ngram_freq = dict()
    out.ngram_prob = dict()

    for n in xrange(out.max_n):
        ngrams = nltk.ngrams(out.words,n+1)
        ngrams = map(" ".join, ngrams)
        freq = nltk.probability.FreqDist(ngrams)
        prob = nltk.probability.MLEProbDist(freq)
        out.ngram_freq[str(n+1)]=dict(freq.items())
        out.ngram_prob[str(n+1)]=dict(zip(freq.iterkeys(),map(prob.prob,freq.iterkeys())))

    return out

def ymd_to_datetime(s):
    return datetime.datetime.utcfromtimestamp(time.mktime(time.strptime(s,"%Y-%m-%d")))

def arxiv_to_article(item, save=False):
    art = Article()

    # Identifiers are a list of unique ids
    art.identifiers = ensure_list(item['identifier'])
    art.title = item['title']

    # Use the first "identifier" that looks like a url
    urls = find_urls(art.identifiers)
    if len(urls)>0: art.url = urls[0]

    # Authors don't change
    art.authors = ensure_list(item['creator'])

    # Latest update is the "published" date
    if item.has_key('date'):
        art.updates = map(ymd_to_datetime,ensure_list(item['date']))
        art.published_on = art.updates[-1]
    art.added_on = datetime.datetime.utcfromtimestamp(time.time())

    # Use sets as tags
    art.tags = dict(zip(ensure_list(item['setSpec']),iter(lambda:1,0)))

    # Use the longest desc as the fulltext description item
    descriptions = ensure_list(item['description'])
    descriptions.sort(lambda x,y: len(y)-len(x))
    art.description = text_to_ngrams(descriptions[0])
    
    # Store the original in metadata just in case
    art.metadata = {'arxiv_original' : dict(item.items())}

    art.validate()
    if save: art.save()
    return art

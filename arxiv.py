import oai, urllib2, time, pymongo, os
""" 
Download all records from the arXiv, store them as raw xml files
and in mongodb
"""

def write_file(file,tree):
    try:
        print "Writing file " + file
        out_file=open(file,'w')
        tree.write(out_file)
        out_file.close()
    except IOError as err:
        print "File writing failed at " + url + ", req " + str(inc)
        print err

def write_mongo(coll, tree):
    try:
        print "Saving records to Mongo"
        coll.insert(oai.iter_records(tree))
    except Exception as err:
        print "Failed to save to Mongo"
        print err

def oai_stream(base_url,verb,token=None,inc=0,prefix="oai_dc",range=None): 
    pause = 20.0
    url = oai.query_url(base_url, verb=verb, range=range, prefix="oai_dc")
    tree = None
    while True:
        if token:
            url = oai.query_url(oai.arxiv, verb=verb, token=token)
        try:
            print "Querying url " + url
            tree = oai.run_query(url)
        except urllib2.HTTPError as err:
            if err.getcode() == 503: # rate limiting
                time.sleep(pause)
                continue
        yield inc, tree
        inc   = inc + 1
        token = oai.resumption_token(tree)
        if token:
            print "Sleeping before resuming for " + str(pause)
            time.sleep(pause)
            continue
        else:
            print "Finished, no resumption token"
            break

def run_stream(out_prefix, mongo_coll, token=None, inc=0):
    for inc, tree in stream_oai_results(oai.arxiv,"ListRecords",token=token,inc=inc):
        out_file = out_prefix + "-records-" + str(inc) + ".xml"
        write_file(out_file, tree)
        write_mongo(mongo_coll, tree)

def run_file(mongo_coll, filename):
    in_file = open(filename)
    tree = oai.objectify.parse(in_file)
    write_mongo(mongo_coll,tree)

if __name__ == "__main__":
    import sys

    if len(sys.argv) not in [2,3]:
        print """Usage:
        arxiv.py --web
        arxiv.py filename.xml
        arxiv.py resumption-token increment-id"""
        exit()

    base_url   = oai.arxiv
    mongo_coll = pymongo.Connection(host='localhost',port=27017).myxiv.arxiv
    out_prefix = './data/arxiv'
    
    if len(sys.argv)==2:
        if os.path.exists(sys.argv[1]):
            run_file(mongo_coll, sys.argv[1])
        elif sys.argv[2]=="--web":
            run_stream(out_prefix, mongo_coll)
    elif len(sys.argv)==3:
        run_stream(out_prefix, mongo_coll, token=sys.argv[1],inc=int(sys.argv[2]))


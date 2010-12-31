import oai, urllib2, time, pymongo
""" 
Download all records from the arXiv, store them as raw xml files
and in mongodb
"""
def write_tree(file,tree):
    out_file=open(file,'w')
    tree.write(out_file)
    out_file.close()

def main(token = None, inc = 0):

    verb= "ListRecords"
    url = oai.query_url(oai.arxiv, verb=verb, prefix="oai_dc")

    pause = 20.0

    out = "./data/arxiv"

    conn = pymongo.Connection(host='localhost',port=27017)
    db   = conn.myxiv
    coll = db.arxiv

    while True:

        if token:
            url = oai.query_url(oai.arxiv, verb=verb, token=token)

        tree = None
        try:
            print "Querying url " + url
            tree = oai.run_query(url)
        except urllib2.HTTPError as err:
            if err.getcode() == 503: # rate limiting
                time.sleep(pause)
                continue
        except Exception as err:
            print err
            exit()

        file = out + "-records-" + str(inc) + ".xml"
        try:
            print "Writing file " + file
            write_tree(file, tree)
            inc = inc+1
        except IOError as err:
            print err
            print inc
            print url
            exit()

        try:
            print "Inserting records into mongo"
            coll.insert(oai.iter_records(tree))
        except Exception as err:
            print err
            exit()

        token = oai.resumption_token(tree)
        if token:
            print "Sleeping before resuming for " + str(pause)
            time.sleep(pause)
            continue
        else:
            print "Finished, no resumption token"
            break

if __name__ == "__main__":
    import sys
    if len(sys.argv)>1:
        main(token=sys.argv[1],inc=int(sys.argv[2]))
    else:
        main()

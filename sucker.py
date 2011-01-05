import arxiv, urllib2, time, pymongo, os, transforms, schema
""" 
Command-line interface to the arxiv client library
"""

def write_file(file, tree):
    out_file=open(file,'w')
    tree.write(out_file)
    out_file.close()

def write_mongo(db, tree):
    schema.connect(db)
    for r in arxiv.oai_records(tree):
        art = transforms.arxiv_to_article(r)
        try:
            art.validate()
            art.save()
        except Exception as e:
            print e

def read_file(filename, inc):
    in_file = open(filename)
    tree = arxiv.parse(in_file)
    in_file.close()
    yield inc, tree

if __name__ == "__main__":
    import sys, optparse
    options = \
        [('-i', 'input', "Input file from which to read XML.  If this is omitted, we read query the web."),
         ('-s', 'start', "YYYY-MM-DD: Start of date range"),
         ('-e', 'end',   "YYYY-MM-DD: End of date range"),
         ('-t', 'token', "Resumption token"),
         ('-o', 'prefix',"Prefix to output files. Resultsets requiring several queries " + \
                            "will save to ./out-n.xml where n is the query number"),
         ('-n', 'inc',   "Output file number to start at"),
         ('-d', 'db',    "MongoDB database to store data in.")]

    parser = optparse.OptionParser(usage="%prog - Command-line interface to the arXiv OAI-PMH interface")

    for (k,dest,help) in options:
        parser.add_option(k,dest=dest,help=help,default=None)
    (opts, args) = parser.parse_args()

    iter     = None
    out_coll = None
    inc = arxiv.parse_inc(opts.inc) 

    if not (opts.prefix or opts.db):
        parser.print_help()
        parser.error("No output specified.")

    if opts.input:
        print "Reading from file: " + opts.input
        iter = read_file(opts.input,inc)
    else:
        print "Reading from web..."
        iter = arxiv.oai_stream(arxiv.arxiv_oai, 
                                verb='ListRecords',
                                range=[opts.start, opts.end],
                                inc=inc,
                                token=opts.token)

    for inc, tree in iter:
        if opts.prefix:
            out_file = opts.output + '-' + str(inc) + ".xml"
            write_file(out_file, tree)
        if opts.db:
            write_mongo(opts.db, tree)


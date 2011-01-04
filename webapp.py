import re
from flask import Flask, request, escape, render_template, config
from schema import myxiv_connect, Article
from datetime import datetime

class config:
        # Articles to show on a page (move this to view)
        max_articles = 20 

        # Connection
        conn = myxiv_connect()

app = Flask(__name__)

# MongoDB connection
class query_builder:
    def __init__(self, s=None):
        self.q = {}
        if s: self.parse(s)

    def t(self,v):
        self.q.update({'tags__'+v:{'$exists':True}})
        return self

    def k(self,v):
        k_all = 'description__words__all'
        k_one = 'description__words'
        if self.q.has_key(k_one):
            self.q.update({k_all:[self.q.pop(k_one),v]})
        elif self.q.has_key(k_all):
            self.q[k_all].append(v)
        else:
            self.q[k_one]=v
        return self

    def y(self,v):
        k = 'published_on__gt'
        if not self.q.has_key(k) or (self.q.has_key(k) and v > self.q[k]):
            self.q['published_on__gt']=datetime(int(v),1,1)
        return self

    def parse(self,s):
        terms = re.compile(r'(t|k|y):([^\s]+)').findall(s)
        map(lambda (k,v): getattr(self,k)(mongo_escape(v)), terms)
        return self

    def get(self):
        return self.q

def mongo_escape(s):
    return s.replace("$","").replace(".","")

def parse_query(s):
    return query_builder(s).get()

@app.route("/")
def index():
    articles = Article.objects.order_by("-published_on")[:config.max_articles]
    return render_template("index.html", articles=articles, num_articles=articles.count()) 

@app.route("/s")
def search():
    q = request.args.get('q','')
    query = parse_query(q)
    articles = Article.objects(**query)[:config.max_articles]
    return render_template("index.html", articles=articles, num_articles=articles.count(), q=q)

if __name__ == "__main__":
    app.run()


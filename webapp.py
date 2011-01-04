import re, datetime as dt, schema as data, search_parser as sp
from flask import Flask, request, escape, render_template, config

class config:
        # Articles to show on a page (move this to view)
        max_articles = 20 
        # Connection
        conn = data.db_connect()

app = Flask(__name__)

@app.route("/")
def index():
    articles = data.Article.objects.order_by("-published_on")[:config.max_articles]
    return render_template("index.html", articles=articles, num_articles=articles.count()) 

@app.route("/s")
def search():
    q = request.args.get('q','')
    query = sp.parse_query(q)
    articles = data.Article.objects(**query)[:config.max_articles]
    return render_template("index.html", articles=articles, num_articles=articles.count(), q=q)

if __name__ == "__main__":
    app.run(debug=True)


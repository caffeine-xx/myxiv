from flask import Flask, render_template
import pymongo

app   = Flask(__name__)
myxiv = pymongo.Connection(host='localhost',port=27017).myxiv
sets  = [s['setSpec'] for s in myxiv.arxiv_sets.find(fields=['setSpec'])]

@app.route("/")
def index():
    articles = myxiv.arxiv.find().limit(20)
    return render_template("index.html", articles=articles, sets=sets) 

@app.route("/y/<int:year>")
def index_year(year):
    articles = myxiv.arxiv.find({'date':{'$gt':str(year),'$lt':str(year+1)}}).sort('date',pymongo.DESCENDING).limit(20) 
    return render_template("index.html", articles=articles, sets=sets) 

@app.route("/s/<set>")
def index_set(set):
    articles = myxiv.arxiv.find({'setSpec':set}).sort('date',pymongo.DESCENDING).limit(20) 
    return render_template("index.html", articles=articles, sets=sets) 

if __name__ == "__main__":
    app.run()


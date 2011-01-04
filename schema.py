from mongoengine import *
import datetime 

def db_connect(db_name='myxiv'):
    db = connect(db_name,host='localhost',port=27017)
    return db

def ensure_article_indices(db):
    unique_idx = ['url','identifiers']
    normal_idx = ['tags','published_on','description.ngram_prob']
    # Indices
    map(lambda i: db.article.ensure_index(i,drop_dups=True),unique_idx)
    map(lambda i: db.article.ensure_index(i,drop_dups=False),normal_idx)

class Ngrams(EmbeddedDocument):
    sentences = ListField(StringField())
    words     = ListField(StringField())
    fulltext = StringField()
    ngram_prob = DictField() 
    ngram_freq = DictField()
    max_n = IntField()

class Article(Document):
    url = StringField()
    identifiers = ListField(StringField())
    authors = ListField(StringField())
    added_on = DateTimeField()
    published_on = DateTimeField()
    updates = ListField(DateTimeField())
    tags = DictField() # {"tag":score}
    title = StringField()
    description = EmbeddedDocumentField(Ngrams)
    metadata = DictField()  # {anything}
    meta = {'indexes': ['url','identifiers','authors','published_on',
                        'added_on','updates','tags','description.ngram_prob']}

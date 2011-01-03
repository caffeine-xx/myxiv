from mongoengine import *

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
                        'added_on','updates','tags']}

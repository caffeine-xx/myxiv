import schema
reload(schema)

def test_myxiv_connect():
    myxiv = schema.db_connect()
    assert myxiv.article.count()>0, "Must have articles"


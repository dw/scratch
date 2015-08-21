
from __future__ import absolute_import
from project import storage


#: Process-global DB connection.
db = None

#: Process-global ModelFactory for a 4-way sharded comments table.
Comments4 = None

#: Process-global ModelFactory for a 6-way sharded comments table.
Comments6 = None


INIT_SQL = """
CREATE TABLE comments0(id PRIMARY KEY NOT NULL, text);
CREATE TABLE comments1(id PRIMARY KEY NOT NULL, text);
CREATE TABLE comments2(id PRIMARY KEY NOT NULL, text);
CREATE TABLE comments3(id PRIMARY KEY NOT NULL, text);

CREATE TABLE comments4(id PRIMARY KEY NOT NULL, text);
CREATE TABLE comments5(id PRIMARY KEY NOT NULL, text);
"""


def setup_db():
    global db, Comments4, Comments6

    comments4 = ['comments0', 'comments1', 'comments2', 'comments3']
    comments6 = comments4 + ['comments4', 'comments5']

    db = storage.open_db(INIT_SQL)
    Comments4 = storage.ModelFactory(comments4, db)
    Comments6 = storage.ModelFactory(comments6, db)


def insert_dummy_comments(factory, n=1024):
    for i in xrange(n):
        model = factory.new()
        model.text = ''
        factory.save(model)


"""
Ultra basic ORM-like wrapper around SQLite3 that handles table sharding.
"""

from __future__ import absolute_import
import sqlite3
import time

from project import clockmap


def row_factory(cursor, tup):
    """
    SQLite row factory that yields dicts.
    """
    return {d[0]: tup[i] for i, d in enumerate(cursor.description)}


def open_db(schema):
    """
    """
    db = sqlite3.connect(':memory:')
    db.row_factory = row_factory
    db.executescript(schema)
    return db


def default_id_func():
    """
    Return a likely-unused integer ID based on the current time in nanoseconds.
    """
    return int(time.time() * 1e9)


class ShardedTable(object):
    """
    Expose primitive SQL operations defined over a single integer primary key
    mapped to a set of tables sharded using clockmap.ClockMap(). Rows are
    represented as dicts.

    :param db:
        sqlite3.Database instance.
    :param cmap:
        clockmap.ClockMap() whose bucket names are table names.
    """
    def __init__(self, db, cmap):
        self.db = db
        self.cmap = cmap

    def rebalance(self):
        """
        Move rows between tables as appropriate to rebalance them following a
        shard map change.

        :return:
            Count of rows that were rebalanced.
        """
        to_move = []
        for _, current_table in self.cmap.get_buckets():
            sql = 'SELECT * FROM %s' % (current_table,)
            for row in self.db.execute(sql):
                expected_table = self.cmap.get_bucket_for_key(str(row['id']))
                if current_table != expected_table:
                    to_move.append((current_table, row))

        for current_table, row in to_move:
            self.save(row)
            sql = 'DELETE FROM %s WHERE id = ?' % (current_table,)
            self.db.execute(sql, (row['id'],))

        return len(to_move)

    def get_by_id(self, id_):
        """
        Fetch a row by primary key, returning its contents as a dict, or None
        if no such row exists.
        """
        assert isinstance(id_, int)
        table = self.cmap.get_bucket_for(str(id_))
        sql = 'SELECT * FROM %s WHERE id = ?' % (table,)
        return next(iter(self.db.execute(sql, (id_,))), None)

    def iter(self):
        """
        Iterate all rows in all tables. Row order is undefined.
        """
        # performs a UNION query, untested whether this is the fast.
        subsql = ['SELECT * FROM %s' % (name,)
                  for _, name in self.cmap.get_buckets()]
        sql = ' UNION '.join(subsql)
        return self.db.execute(sql)

    def get_shard_counts(self):
        """
        Return a row count for each shard.

        :return:
            List of (shard name, count).
        """
        subsql = ['SELECT \'%s\' name, COUNT(*) cnt FROM %s' % (name, name)
                  for _, name in self.cmap.get_buckets()]
        sql = ' UNION '.join(subsql)
        return sorted((row['name'], row['cnt'])
                      for row in self.db.execute(sql))

    def save(self, row):
        """
        Create or update a row in the appropriate shard.

        :param row:
            Dict describing row, including `id` key.
        """
        assert isinstance(row['id'], int)
        values = row.values()
        colspec = ', '.join(row.keys())
        valuespec = ', '.join(['?'] * len(row))
        table = self.cmap.get_bucket_for_key(str(row['id']))
        sql = 'REPLACE INTO %s(%s) VALUES (%s)' % (table, colspec, valuespec)
        self.db.execute(sql, values)

    def delete(self, id_):
        """
        Delete a row from the appropriate shard if it exists.
        """
        assert isinstance(id_, int)
        table = self.cmap.get_bucket_for(str(id_))
        sql = 'DELETE FROM %s WHERE id = ?' % (table,)
        self.db.execute(sql, (id_,))


class Model(object):
    """
    Expose a database row's fields as attributes. On save, if the row does not
    have an ID, one is assigned using the associated model's ID factory.
    """
    def __init__(self, factory, dct=None):
        vars(self)['factory'] = factory
        vars(self)['_dct'] = dct or {}

    def __getattr__(self, key):
        """
        Map attribute gets to dict key lookups, returning None if a key does
        not exist.
        """
        return self._dct.get(key)

    def __setattr__(self, key, value):
        """
        Map attribute sets to dict key sets.
        """
        self._dct[key] = value

    def save(self):
        self.factory.save(self)


class ModelFactory(object):
    """
    Bind a set of sharded tables in a SQLite3 database instance to an
    associated ID factory and Model subclass, with methods to map between raw
    SQL rows and model instances.

    :param tables:
        String list of table names the models are sharded over.
    :param db:
        SQLite3 database instance.
    :param id_factory:
        Primary key generator function.
    :param model_factory:
        Model subclass.
    """
    def __init__(self, tables, db,
                 id_factory=default_id_func,
                 model_factory=Model):
        self._tables = tables
        self._db = db
        self._id_factory = id_factory
        self._model_factory = model_factory
        self._cmap = clockmap.ClockMap()
        self._cmap.add_buckets(tables)
        self._stable = ShardedTable(self._db, self._cmap)

    def rebalance(self):
        """
        Move models between tables as appropriate to rebalance them following a
        shard map change.

        :return:
            Count of models that were rebalanced.
        """
        return self._stable.rebalance()

    def get_shard_counts(self):
        """
        Return a row count for each shard.

        :return:
            List of (shard name, count).
        """
        return self._stable.get_shard_counts()

    def new(self, dct=None):
        """
        Model instance factory. If `dct` is supplied, represents the contents
        of the model's row.
        """
        return self._model_factory(self, dct)

    def iter(self):
        """
        Iterate all models in the database.
        """
        return (self.new(dct) for dct in self._stable.iter())

    def get_object_by_id(self, id_):
        """
        Fetch a model by its primary key, or None.
        """
        dct = self._stable.get_by_id(id_)
        if dct is not None:
            return self.new(dct)

    def save(self, model):
        """
        Write a model to the database. If the model has no ID, one is assigned
        using `:py:attr:_id_factory`.
        """
        dct = model._dct
        dct.setdefault('id', self._id_factory())
        self._stable.save(model._dct)

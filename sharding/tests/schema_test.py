'''
PYTHONPATH=. python tests/schema_test.py
'''

from __future__ import absolute_import
import unittest

from project import schema


class Test(unittest.TestCase):
    def test_0(self):
        schema.setup_db()

        print 'Inserting 1024 dummy rows...'
        schema.insert_dummy_comments(schema.Comments4, n=1024)
        print

        print 'Row-per-shard count prior to rebalance:'
        for shard, count in schema.Comments4.get_shard_counts():
            print '%s: %d' % (shard, count)

        smin = min(c for _, c in schema.Comments4.get_shard_counts())
        smax = max(c for _, c in schema.Comments4.get_shard_counts())
        print 'Variance: %.2f%%' % (smin/float(smax))
        print

        print 'Rebalancing...'
        moved = schema.Comments6.rebalance()
        print 'Number of comments requiring move: %d' % (moved,)
        print

        print 'Row-per-shard count after rebalance:'
        for shard, count in schema.Comments6.get_shard_counts():
            print '%s: %d' % (shard, count)

        smin = min(c for _, c in schema.Comments6.get_shard_counts())
        smax = max(c for _, c in schema.Comments6.get_shard_counts())
        print 'Variance: %.2f%%' % (smin/float(smax))
        print


if __name__ == '__main__':
    unittest.main()

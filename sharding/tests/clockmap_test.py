
from __future__ import absolute_import
import unittest

from project import clockmap


class Test(unittest.TestCase):
    def test_0(self):
        cmap = ClockMap()
        cmap.add_buckets(['shard1', 'shard2', 'shard3', 'shard4'])
        print cmap.get_buckets()

        c = collections.Counter()
        for x in range(1024):
            c[cmap.get_bucket_for_key(str(x))] += 1

        print c

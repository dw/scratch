
from __future__ import absolute_import
import bisect
import collections
import hashlib


class ClockMap(object):
    """
    Consistent hashing around a clock face.

    :param exp:
        Exponent used to select number of ticks on the clock face (2**n) and to
        calculate the mask used to select a bucket (2**n-1). Default exp=10
        gives 10 bits, or 1024 buckets.
    """
    def __init__(self, exp=10):
        assert isinstance(exp, int)
        self.exp = exp
        self.mask = 2**exp-1
        self.ticks = 2**exp
        self.starts = []
        self.names = []

    def _modulo(self, key):
        """
        Given some str or bytes object, return an integer representing the
        bucket associated with the hash of its content.
        """
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        return int(hashlib.md5(key).hexdigest(), 16) & self.mask

    def add_bucket(self, start, name):
        """
        Define a new bucket named `name` starting at `start` and continuing
        until the next defined bucket, wrapping around the clockface until one
        is found.

        :param start:
            Starting index, 0..(2**exp-1).
        :param name:
            Bucket name.
        """
        assert start < self.ticks
        idx = bisect.bisect_left(self.starts, start)
        if idx < len(self.starts) and self.starts[idx] == start:
            raise ValueError('Segment %d.. already exists.' % (start,))
        self.starts.insert(idx, start)
        self.names.insert(idx, name)

    def add_buckets(self, names):
        """
        Create buckets to as evenly as possible divide the clockface amongst
        the given names.

        :param names:
            List of bucket names.
        """
        if self.ticks < len(names):
            raise ValueError("More buckets defined than available ticks.")

        each = self.ticks / len(names)
        for start, name in zip(xrange(0, self.ticks, each), names):
            self.add_bucket(start, name)

    def get_buckets(self):
        """
        Return a list of tuples describing configured buckets.
        """
        return [(self.starts[i], name)
                for i, name in enumerate(self.names)]

    def get_bucket_for_key(self, key):
        """
        Given a string, return the name of the segment storing its hash value.
        """
        assert len(self.starts) > 0
        m = self._modulo(key)
        idx = bisect.bisect_left(self.starts, m)
        if idx == len(self.starts):  # Wrap as necessary.
            idx = 0
        return self.names[idx]

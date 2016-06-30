
from __future__ import absolute_import
import unittest
import gulp.structures


class RingBufferTestCase(unittest.TestCase):
    klass = gulp.structures.RingBuffer

    def setUp(self):
        self.buf = self.klass(size=3)

    def test_empty_get_returns_none(self):
        assert self.buf.get() is None

    def test_empty_peek_returns_none(self):
        assert self.buf.peek() is None

    def test_partial_get_returns_val_then_none(self):
        self.buf.put(1)
        assert self.buf.get() == 1
        assert self.buf.get() is None
        assert self.buf.get() is None
        assert self.buf.get() is None

    def test_overflow_advances_read_head(self):
        self.buf.put(1)
        self.buf.put(2)
        self.buf.put(3)
        self.buf.put(4)
        assert self.buf.get() == 2
        assert self.buf.get() == 3
        assert self.buf.get() == 4
        assert self.buf.get() is None


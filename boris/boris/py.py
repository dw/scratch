
from __future__ import absolute_import


def add_repr(attrs=None):
    def wrapper(cls):
        qname = '%s.%s' % (cls.__module__, cls.__name__)
        def __repr__(self):
            bits = []
            if attrs:
                for attr in attrs:
                    value = getattr(self, attr, None)
                    if value is not None:
                        bits.append('%s:%r' % (attr, value))
            if bits:
                return '<%s %s>' % (qname, ' '.join(bits))
            else:
                return '<%s>' % (qname,)
        cls.__repr__ = __repr__
        return cls
    return wrapper


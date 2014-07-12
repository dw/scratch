

class MustFinalize(object):
    obj = None
    succeed = None
    fail = None

    def __enter__(self):
        return self.obj

    def __exit__(self, etype, evalue, etb):
        if etype:
            self.fail()
        else:
            self.succeed()

    def __getattr__(self, key):
        raise RuntimeError("with: statement required to access %r" %
                           (self.obj,))

    def __repr__(self):
        return '<wrapped %r>' % (self.obj,)


def must_finalize(obj, succeed, fail=None):
    mf = MustFinalize()
    mf.obj = obj
    mf.succeed = succeed
    mf.fail = fail or succeed
    return mf


class MyObject(object):
    def start(self):
        pass
    def stop(self):
        pass


do_nothing = lambda: None
myo = must_finalize(MyObject(), do_nothing)



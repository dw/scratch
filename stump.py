
from __future__ import absolute_import
import collections
import itertools
import os
import resource
import signal
import sys
import thread
import time


INDEX_HTML = '''
<input type=range>


<table id="hotfuncs">
</table>

'''


class Profiler(object):
    max_depth = 16
    samples = 0

    def _sigprof(self, _, me_frame):
        w = self.out.write
        ch = self.ch
        fh = self.fh
        self.samples += 1

        ru = resource.getrusage(resource.RUSAGE_SELF)
        w(str(time.time())); w(' ')
        w(str(ru.ru_utime)); w(' ')
        w(str(ru.ru_stime)); w('\n')

        frames = sys._current_frames()
        frames[thread.get_ident()] = me_frame
        for tid, frame in frames.iteritems():
            w(str(tid)); w('\n')
            while frame:
                code = frame.f_code
                ckey = (code, code.co_filename, code.co_firstlineno, code.co_name)
                if ckey not in ch:
                    # co_filename descriptor returns new string on each
                    # invocation, so ID changes. 'intern' the first.
                    s = fh.get(code.co_filename)
                    if s is None:
                        w('file ')
                        s = code.co_filename
                        w(str(id(s)))
                        w(' ')
                        w(code.co_filename)
                        w('\n')
                        fh[s] = intern(s)

                    w('code ')
                    w(str(id(code)))
                    w(' ')
                    w(str(id(s)))
                    w(' ')
                    w(str(code.co_firstlineno))
                    w(' ')
                    w(code.co_name)
                    w('\n')
                    ch.add(ckey)

                w(str(id(code)))
                w(' ')
                w(str(frame.f_lineno))
                w('\n')
                frame = frame.f_back
            w('\n')
        w('\n')

    def start(self):
        self.out = open('profiler.out', 'w', 64 * 1024)
        self.ch = set()
        self.fh = {}

        self.write = self.out.write
        self.sig, self.tim = signal.SIGPROF, signal.ITIMER_PROF
        self.sig, self.tim = signal.SIGALRM, signal.ITIMER_REAL

        signal.signal(self.sig, self._sigprof)
        signal.setitimer(self.tim, 0.01, 0.01)

    def stop(self):
        signal.signal(self.sig, signal.SIG_IGN)
        signal.setitimer(self.tim, 0, 0)
        self.out.close()


def parse_frame(stack, line, trace):
    s = line()
    if s == '\n':
        return False

    if s.startswith('file'):
        bits = s.split(' ', 2)
        trace.files[int(bits[1])] = bits[2].rstrip()
    elif s.startswith('code'):
        bits = s.split(' ', 4)
        filename = trace.files[int(bits[2])]
        firstline = int(bits[3])
        trace.codes[int(bits[1])] = filename, firstline, bits[4].rstrip()
    else:
        bits = s.split(' ', 1)
        code = trace.codes[int(bits[0])]
        lineno = int(bits[1])
        stack.append((code, lineno))
    return True


def parse_thread(line, trace):
    s = line()
    if s == '\n':
        return False

    stack = []
    trace.threads.setdefault(int(s), []).append(stack)
    while parse_frame(stack, line, trace):
        pass
    return True


def parse_sample(line, trace):
    s = line()
    if not s:
        return False

    stamp = float(s)
    usertime = float(line())
    systime = float(line())
    trace.timing.append((stamp, usertime, systime))
    while parse_thread(line, trace):
        pass

    return True


class Trace:
    files = {}
    codes = {}
    timing = []
    threads = {}
    min_stamp = None
    max_stamp = None
    samples = 0


def parse():
    fp = open('profiler.out')
    line = fp.readline

    trace = Trace()
    while parse_sample(line, trace):
        trace.samples += 1

    trace.min_stamp = trace.timing[0][0]
    trace.max_stamp = trace.timing[-1][0]
    return trace


def get_annotation(trace, filename, start=None, stop=None):
    if start is None:
        start = 0
    if stop is None:
        stop = trace.samples - 1

    counts = collections.Counter()
    for tid, stacks in trace.threads.iteritems():
        for stack in itertools.islice(stacks, start, stop):
            for code, lineno in stack:
                if code[0] == filename:
                    counts[lineno] += 1

    lines = open(filename).readlines()
    return {
        'samples': [counts.get(i, 0) for i in xrange(len(lines))],
        'lines': lines
    }


def get_hotstuff(trace, start=None, stop=None, n=50):
    if start is None:
        start = 0
    if stop is None:
        stop = trace.samples - 1

    funcfirst = {}
    hotfuncs = collections.Counter()
    hotfiles = collections.Counter()
    funcline = {}

    for sample, (tid, stacks) in enumerate(trace.threads.iteritems()):
        for stack in itertools.islice(stacks, start, stop):
            for depth, (code, lineno) in enumerate(stack):
                funcfirst.setdefault(code, sample)
                hotfuncs[code] += 1
                hotfiles[code[0]] += 1

    for key in hotfuncs:
        scale = funcfirst[key] / float(trace.samples)
        hotfuncs[key] *= scale

    return {
        'hotfuncs': hotfuncs.most_common(n),
        'hotfiles': hotfiles.most_common(n)
    }


def hottest():
    print 'parsing'
    trace = parse()
    print 'summing'
    hotstuff = get_hotstuff(trace)

    print
    print 'hotfuncs'
    for code in hotstuff['hotfuncs']:
        print code

    print
    print 'hotfiles'
    for filename in hotstuff['hotfiles']:
        print filename


def heatplot():
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    import numpy as np

    print 'parse'
    trace = parse()

    print 'plot'
    dims = (len(trace.codes), trace.samples)
    print dims
    ar = np.zeros(dims)
    seen = {}
    lco = 0

    window = 100 * 1

    for tid, stacks in trace.threads.iteritems():
        for sample, stack in enumerate(stacks):
            for code, lineno in stack:
                if code not in seen:
                    seen[code] = lco
                    lco += 1
                x = seen[code]
                y = sample
                ar[x, y] = 1.0 - (ar[x, (y-window):y]).mean()

    print 'render'
    global imgplot

    import matplotlib.cm as cm
    cmap = cm.get_cmap('bone')

    imgplot = plt.imshow(ar, cmap=cmap)
    imgplot.write_png('a.png', noscale=True)



def serve():
    trace = parse()

    import bottle
    app = bottle.Bottle()
    @app.get('/')
    def index():
        return INDEX_HTML

    def getint(n):
        if n in bottle.request.query:
            return int(bottle.request.query[n])

    @app.get('/annotate')
    def do_annotate():
        start = getint('start')
        stop = getint('stop')
        return get_annotation(trace, bottle.request.query['filename'],
                              start=start, stop=stop)

    @app.get('/hotstuff')
    def do_get_hotstuff():
        return get_hotstuff(trace)

    @app.get('/info')
    def get_info():
        return {
            'min_stamp': trace.min_stamp,
            'max_stamp': trace.max_stamp,
            'numfiles': len(trace.files),
            'numcodes': len(trace.codes),
            'samples': trace.samples
        }

    @app.get('/threads')
    def get_threads():
        return {
            'threads': threads.keys()
        }

    app.run(reloader=True)


def trace():
    args = sys.argv[2:]
    sys.argv[:] = args
    progname = args[0]
    sys.path.insert(0, os.path.dirname(progname))
    with open(progname, 'rb') as fp:
        code = compile(fp.read(), progname, 'exec')

    globs = {
        '__file__': progname,
        '__name__': '__main__',
        '__package__': None,
    }
    p = Profiler()
    p.start()
    try:
        exec code in globs, None
    finally:
        p.stop()
        print 'stump.py: %d samples in %d funcs from %d files' %\
              (p.samples, len(p.ch), len(p.fh))


def main():
    if sys.argv[1] == 'trace':
        trace()
    elif sys.argv[1] == 'serve':
        serve()
    elif sys.argv[1] == 'heatplot':
        heatplot()
    elif sys.argv[1] == 'hottest':
        hottest()


if __name__ == '__main__':
    main()

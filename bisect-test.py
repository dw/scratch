
# http://pythonsweetness.tumblr.com/post/74073984682/cowboy-optimization-bisecting-a-function

import math
import time
import zlib

import sortedfile

target = 3000
lines = sorted(file('/usr/share/dict/words'))

print 'input len:', len(lines)
print 'input avgsize:', sum(map(len, lines)) / float(len(lines))
print 'input steps:', math.log(len(lines), 2)
print 'target size:', target
print

steps = [0]

def compo(i):
    dat = zlib.compress(''.join(lines[:i]))
    actual = len(dat)
    ratio = actual/float(target)
    out = (ratio, dat)
    print[i, actual, ratio]
    steps[0]+=1
    return out


t0 = time.time()

doink = sortedfile.bisect_func_right((1.0,), 1, len(lines), compo)

maxlines, (ratio, output) = doink
if maxlines and (ratio > 1.0):
    maxlines -= 1
    ratio, output = compo(maxlines)

print
print 'time taken:', 1000 * (time.time() - t0)
print 'output steps:', steps
print 'maxlines:', maxlines
print 'maxlines len:', sum(map(len, lines[:maxlines]))
print 'target ratio:', ratio
print 'outlen:', len(output)

#print compo(50, (15000,))

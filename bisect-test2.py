
# http://pythonsweetness.tumblr.com/post/74073984682/cowboy-optimization-bisecting-a-function

import math
import time
import zlib

import sortedfile

maxcomp = 8
target = 8000

lines = file('/usr/share/dict/words').readlines()

line_count = len(lines)
line_sum = sum(map(len, lines))
line_avg = float(line_sum) / line_count
ubound = int(target / line_avg) * maxcomp

print 'input len:', len(lines)
print 'max comp:', maxcomp
print 'ubound:', ubound
print 'input avgsize:', sum(map(len, lines)) / float(len(lines))
print 'input steps:', math.log(len(lines), 2), 'all /', math.log(ubound,2), 'ubound'
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

doink = sortedfile.bisect_func_right((1.0,), 1, ubound, compo)

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
print 'compression ratio:', sum(map(len, lines[:maxlines])) / float(len(output))
print 'outlen:', len(output)

#print compo(50, (15000,))

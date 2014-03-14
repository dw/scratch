
# http://pythonsweetness.tumblr.com/post/74073984682/cowboy-optimization-bisecting-a-function

import math
import time
import zlib

import sortedfile

maxcomp = 10
target = 4000

lines = []
line_sum = 0
for line in file('/Users/dmw/messages'):
    lines.append(line)
    line_sum += len(line)
    line_avg = float(line_sum) / len(lines)
    if ((len(lines) * line_avg) / maxcomp) > target:
        break

print 'input len:', len(lines)
print 'max comp:', maxcomp
print 'input avgsize:', line_avg
print 'input steps:', math.log(len(lines), 2)
print 'target size:', target
print

steps = [0]
cac = {}

def compo(i):
    output = zlib.compress(''.join(lines[:i]))
    cac[i] = output
    print [i, len(output) - target]
    steps[0] += 1
    return len(output) - target


t0 = time.time()

maxlines, actual = sortedfile.bisect_func_right(0, 1, len(lines), compo)
maxlines -= 1
output = cac[maxlines]

print
print 'time taken:', 1000 * (time.time() - t0)
print 'output steps:', steps
print 'maxlines:', maxlines
print 'maxlines len:', sum(map(len, lines[:maxlines]))
print 'compression ratio:', sum(map(len, lines[:maxlines])) / float(len(output))
print 'outlen:', len(output)

#!/usr/bin/env python

import random
import threading
import time

sz = 4096
ubound = (750153891840 / sz) - 1

tot = 0
tim = 0.0

now = lambda: time.time() * 1000

def go():
    global tot, tim
    buf = bytearray(sz)
    fp = file('/dev/md0', 'r', 0)
    while True:
        off = random.randint(0, ubound) * sz
        t0 = now()
        fp.seek(off)
        fp.readinto(buf)
        tim += now() - t0
        tot += 1

for x in range(32):
    t = threading.Thread(target=go)
    t.setDaemon(True)
    t.start()

while True:
    s = now()
    time.sleep(1)
    e = now()
    a = tot
    b = tim
    print a, (e - s) / a, b / a, (a * sz) / 1024., 'k/sec'
    tot -= a
    tim -= b

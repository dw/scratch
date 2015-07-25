
import os
import socket
import sys


addr = ('127.1', 6969)
pool_size = 8

def connect_loop(i):
    while True:
        s = socket.socket()
        try:
            s.connect(addr)
        except socket.error, e:
            print '%d: exit due to %s' % (i, e)
            return 0

        try:
            ss = s.recv(64)
        except socket.error, e:
            print '%d: %s' % (i, e)
            return -1

for i in xrange(pool_size):
    if not os.fork():
        sys.exit(connect_loop(i))

for _ in xrange(pool_size):
    print ['child exit', os.waitpid(-1, 0)]

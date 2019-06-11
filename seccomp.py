# The MIT License (MIT)
# 
# Copyright (c) 2015 David Wison
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import ctypes
import json
import os
import resource
import signal
import socket
import struct

_libc = ctypes.CDLL(None)
_exit = _libc._exit
_prctl = _libc.prctl

PR_SET_SECCOMP = 22
SECCOMP_MODE_STRICT = 1


def enable_seccomp():
    rc = _prctl(PR_SET_SECCOMP, SECCOMP_MODE_STRICT, 0)
    assert rc == 0


def read_exact(fp, n):
    buf = ''
    while len(buf) < n:
        buf2 = os.read(fp.fileno(), n)
        if not buf2:
            _exit(123)
        buf += buf2
    return buf2

def write_exact(fp, s):
    done = 0
    while done < len(s):
        written = os.write(fp.fileno(), s[done:])
        if not written:
            _exit(123)
        done += written

class SecureEvalHost(object):
    def __init__(self):
        self.host, self.child = socket.socketpair()
        self.pid = None

    def start_child(self):
        assert not self.pid
        self.pid = os.fork()
        if not self.pid:
            self._child_main()
        self.child.close()

    def kill_child(self):
        assert self.pid
        pid, status = os.waitpid(self.pid, os.WNOHANG)
        os.kill(self.pid, signal.SIGKILL)

    def do_eval(self, msg):
        return {'result': eval(msg['body'])}

    def _child_main(self):
        self.host.close()
        for fd in map(int, os.listdir('/proc/self/fd')):
            if fd != self.child.fileno():
                try:
                    os.close(fd)
                except OSError:
                    pass

        resource.setrlimit(resource.RLIMIT_CPU, (1, 1))
        enable_seccomp()
        while True:
            sz, = struct.unpack('>L', read_exact(self.child, 4))
            doc = json.loads(read_exact(self.child, sz))
            if doc['cmd'] == 'eval':
                resp = self.do_eval(doc)
            elif doc['cmd'] == 'exit':
                _exit(0)
            goobs = json.dumps(resp)
            write_exact(self.child, struct.pack('>L', len(goobs)))
            write_exact(self.child, goobs)

    def eval(self, s):
        msg = json.dumps({'cmd': 'eval', 'body': s})
        write_exact(self.host, struct.pack('>L', len(msg)))
        write_exact(self.host, msg)
        sz, = struct.unpack('>L', read_exact(self.host, 4))
        goobs = json.loads(read_exact(self.host, sz))
        return goobs['result']


def go():
    sec = SecureEvalHost()
    sec.start_child()
    try:
        print sec.eval('1+1')
    finally:
        sec.kill_child()

if __name__ == '__main__':
    go()

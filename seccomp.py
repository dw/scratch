
# pip install python-prctl cffi

import json
import os
import resource
import signal
import socket
import struct

import cffi
import prctl

_ffi = cffi.FFI()
_ffi.cdef('void _exit(int);')
_libc = _ffi.dlopen(None)

def _exit(n=1):
    """Invoke _exit(2) system call."""
    _libc._exit(n)

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
        for fd in xrange(1024):
            if fd != self.child.fileno():
                try:
                    os.close(fd)
                except OSError:
                    pass

        resource.setrlimit(resource.RLIMIT_CPU, (1, 1))
        prctl.set_seccomp(True)
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


sec = SecureEvalHost()
sec.start_child()
print sec.eval('1+1')
sec.kill_child()

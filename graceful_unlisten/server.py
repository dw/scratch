#
# UNIX close()/shutdown()/accept() do not permit draining pending ESTABLISHED
# connections from a TCP listener's backlog. Invoking close() will immediatley
# cause RSTs to be sent to each pending connection that has yet to be
# accept()'d, causing client applications to receive an apparently successful
# connection that immediately disconnects, rather than simply a connect timeout
# or ECONNREFUSED.
#
# There is no way using the POSIX APIs to avoid this, however on Linux since we
# can attach a BPF filter to any socket, we can leave the socket in the
# listening state while preventing further pending connections from being
# established. While the filter is attached, we can gracefully process the
# remaining connection backlog before finally closing the now-drained socket.
#

import ctypes
import os
import select
import socket

SO_ATTACH_FILTER = 26

class BpfProgram(ctypes.Structure):
    _fields_ = [
        ('bf_len', ctypes.c_int),
        ('bf_insns', ctypes.c_void_p)
    ]

class BpfInstruction(ctypes.Structure):
    _fields_ = [
        ('code', ctypes.c_uint16),
        ('jt', ctypes.c_uint8),
        ('jf', ctypes.c_uint8),
        ('k', ctypes.c_uint32),
    ]

def attach_reject_filter(sock):
    insn = BpfInstruction()
    insn.code = 0x06        # RET
    insn.k = 0x0            # Reject

    prog = BpfProgram()
    prog.bf_len = 1         # Opcode count
    prog.bf_insns = ctypes.addressof(insn)

    sock.setsockopt(socket.SOL_SOCKET, SO_ATTACH_FILTER, buffer(prog))

def is_backlog_empty(sock):
    rfds, _, _ = select.select([sock.fileno()], [], [], 0.0)
    return len(rfds) == 0


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('127.1', 6969))

# Listen and accept clients for a while.
s.listen(5)

# However existing client connections continue to function normally.
while not os.path.exists('stop'):
    client, _ = s.accept()
    client.send('OK\n')
    client.close()

if file('stop').read().startswith('graceful'):
    # Time to shutdown. Attach the filter. SYN sent to the listening port will
    # be dropped by the kernel.
    attach_reject_filter(s)

    while not is_backlog_empty(s):
        print 'backlog!'
        client, _ = s.accept()
        client.send('OK\n')
        client.close()

s.close()

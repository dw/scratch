
import socket
import sys


def set_keepalive(sock, interval=1, probes=5):
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, interval)
    if hasattr(socket, 'TCP_KEEPCNT'):
        sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, probes)
    if hasattr(socket, 'TCP_KEEPIDLE'):
        sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, interval)
    if hasattr(socket, 'TCP_KEEPINTVL'):
        sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, interval)


s = socket.socket()
s.bind(('', 0))
print s.getsockname()
set_keepalive(s)
s.listen(1)

while True:
    csock, addr = s.accept()
    set_keepalive(csock)
    print csock.recv(512)

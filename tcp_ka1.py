
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
set_keepalive(s)
s.connect(('api.somehost.com', 80))
set_keepalive(s)
print 'here'
s.send('HEAD / HTTP/1.1\r\nHost: api.somehost.com\r\n\r\n')
print s.recv(2048)
while True:
    ss = raw_input()
    s.send(ss)
    print s.recv(2048)

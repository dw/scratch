
from __future__ import absolute_import

import os
os.environ['PYTHONINSPECT'] = '1'
from pdb import pm

import ctypes
import socket
import struct
import subprocess
import random
from pprint import pprint


SO_ATTACH_FILTER = 26


class BpfProgram(ctypes.Structure):
    _fields_ = [
        ('bf_len', ctypes.c_int),
        ('bf_insns', ctypes.c_void_p)
    ]


class EthernetHeader(ctypes.BigEndianStructure):
    _fields_ = [
        ('src', ctypes.c_ubyte * 6),
        ('dst', ctypes.c_ubyte * 6),
        ('type', ctypes.c_uint16)
    ]


class IpHeader(ctypes.BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('version', ctypes.c_ubyte, 4),
        ('header_length', ctypes.c_ubyte, 4),
        ('dscp', ctypes.c_ubyte, 6),
        ('ecn', ctypes.c_ubyte, 2),
        ('total_length', ctypes.c_uint16),
        ('ipid', ctypes.c_uint16),
        ('flags', ctypes.c_uint16, 3),
        ('frag_offset', ctypes.c_uint16, 13),
        ('ttl', ctypes.c_uint8),
        ('protocol', ctypes.c_uint8),
        ('checksum', ctypes.c_uint16),
        ('src', ctypes.c_uint32),
        ('dst', ctypes.c_uint32)
    ]


class TcpHeader(ctypes.BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('sport', ctypes.c_uint16),
        ('dport', ctypes.c_uint16),
        ('seq', ctypes.c_uint32),
        ('ack', ctypes.c_uint32),

        ('data_offset', ctypes.c_uint16, 4),
        ('reserved', ctypes.c_uint16, 3),
        ('ns', ctypes.c_uint16, 1),
        ('cwr', ctypes.c_uint16, 1),
        ('ece', ctypes.c_uint16, 1),
        ('urg', ctypes.c_uint16, 1),
        ('ack', ctypes.c_uint16, 1),
        ('psh', ctypes.c_uint16, 1),
        ('rst', ctypes.c_uint16, 1),
        ('syn', ctypes.c_uint16, 1),
        ('fin', ctypes.c_uint16, 1),

        ('window_size', ctypes.c_uint16),
        ('checksum', ctypes.c_uint16),
        ('urg_ptr', ctypes.c_uint16),
        ('options', ctypes.c_ubyte*40)
    ]


def compile_expr(s):
    proc = subprocess.Popen(stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            args=['tcpdump', '-ddd', s])
    stdout, stderr = proc.communicate()
    lines = stdout.splitlines()
    if not lines[0].rstrip().isdigit():
        raise RuntimeError('tcpdump: ' + stderr)

    length = int(lines[0])
    return length, ''.join(struct.pack('=HBBL', *map(int, l.split()))
                           for l in lines[1:])


def attach_filter(sock, expr):
    length, compiled = compile_expr(expr)
    cbuf = ctypes.create_string_buffer(compiled)

    prog = BpfProgram()
    prog.bf_len = length
    prog.bf_insns = ctypes.addressof(cbuf)

    sock.setsockopt(socket.SOL_SOCKET, SO_ATTACH_FILTER, buffer(prog))


def dump(o):
    flds = [x[0] for x in type(o)._fields_]
    print ([(n, getattr(o, n)) for n in flds])


def checksum1(o, s=0):
    s += o
    s = (s & 0xffff) + (s >> 16)
    return ~s & 0xffff


def checksum(ba, start, end, s=0):
    for i in xrange(start, end, 2):
        s += ba[i] + (ba[i+1] << 8)
        s = (s & 0xffff) + (s >> 16)
    return ~s & 0xffff


def tcp_checksum(ba):
    s = checksum(ba, 14 + 12, 14 + 20)
    s = checksum1(0, s)
    s = checksum1(6, s)
    s = checksum
    pass

conns = {}

def handshake1(addr):
    isn = random.randint(0, 0xffffffff)
    tcp = {
        'addr': addr,
        'func': handshake2,
        'risn': itcphdr.seq,
        'rseq': itcphdr.seq + 1,
        'wisn': isn,
        'wseq': isn
    }
    conns[addr] = tcp

    oethhdr.src = iethhdr.dst
    oethhdr.dst = iethhdr.src
    oethhdr.type = 0x800

    oiphdr.version = 4
    oiphdr.header_length = 4
    oiphdr.total_length = 64
    oiphdr.ttl = 255
    oiphdr.ipid = iiphdr.ipid
    oiphdr.dst = iiphdr.src
    oiphdr.src = iiphdr.dst

    oiphdr.checksum = 0
    oiphdr.checksum = checksum(odata, 14, 34)

    otcphdr.sport = itcphdr.dport
    otcphdr.dport = itcphdr.sport
    otcphdr.seq = tcp['wseq']
    otcphdr.seq = tcp['rseq']
    otcphdr.data_offset = 5
    otcphdr.syn = 1
    otcphdr.ack = 1
    otcphdr.window_size = 0xffff

    tcp_checksum()

    print 'out',
    dump(oethhdr)
    print 'out',
    dump(oiphdr)


def handshake2(d):
    pass


idata = bytearray(4000)
iethhdr = EthernetHeader.from_buffer(idata, 0)
iiphdr = IpHeader.from_buffer(idata, 14)
itcphdr = TcpHeader.from_buffer(idata, 34)

odata = bytearray(4000)
oethhdr = EthernetHeader.from_buffer(idata)
oiphdr = IpHeader.from_buffer(odata, 14)
otcphdr = TcpHeader.from_buffer(odata, 34)

sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, 0x0800)
attach_filter(sock, 'dst host 178.63.48.10 and port 1800')
sock.bind(('eth0', 0x0800))

while 1:
    length = sock.recv_into(idata)
    print
    dump(iethhdr)
    dump(iiphdr)
    dump(itcphdr)
    addr = (iiphdr.src, itcphdr.sport)
    d = conns.get(addr)
    if d:
        d['func'](d)
    else:
        handshake1(addr)

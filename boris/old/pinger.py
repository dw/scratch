
import array
import os
import time

import socket
import ctypes


def microsecs():
    return int(time.time() * 1e6)


def inet_checksum(s):
    if len(s) & 1:
        s += '\0'
    n = sum(array.array('H', s))
    n = (n >> 16) + (n & 0xffff)
    n = n + (n >> 16)
    return (~n) & 0xffff


def dump(obj, depth=1):
    if depth == 1:
        print ('  '*(depth-1)) + (type(obj).__name__) + ':'
    pad = '  '*depth
    for field in obj._fields_:
        name, klass = field[:2]
        val = getattr(obj, name)
        if issubclass(klass, ctypes.Structure):
            print pad+name+':'
            dump(val, depth=depth+1)
        elif issubclass(klass, ctypes.Array):
            print pad+name+': '+repr(val[:])
        else:
            print pad+name+': '+repr(val)
    if depth == 1:
        print


class IpHeader(ctypes.Structure):
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
        ('src', ctypes.c_ubyte*4),
        ('dst', ctypes.c_ubyte*4)
    ]


class EchoHeader(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('type', ctypes.c_ubyte),
        ('code', ctypes.c_ubyte),
        ('checksum', ctypes.c_uint16),
        ('identifier', ctypes.c_uint16),
        ('sequence', ctypes.c_uint16),
        ('data_usecs', ctypes.c_uint64),
    ]


class IpAndEchoHeader(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('ip', IpHeader),
        ('icmp', EchoHeader),
    ]

outbuf = ctypes.create_string_buffer(ctypes.sizeof(EchoHeader))
icmph = EchoHeader.from_buffer(outbuf)
icmph.type = 8
icmph.code = 0
icmph.data_usecs = microsecs()
icmph.checksum = inet_checksum(outbuf[:])

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_ICMP)
s.sendto(outbuf, 0, ('127.0.0.1', 0))
msg = s.recv(512)
osx_ping = IpAndEchoHeader.from_buffer_copy(msg)
dump(osx_ping)

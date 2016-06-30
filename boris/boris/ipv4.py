
from __future__ import absolute_import
import array
import ctypes
import socket
import struct


def addr_to_int(addr):
    s = socket.inet_aton(addr)
    return struct.unpack('=L', s)[0]


def int_to_addr(n):
    s = struct.pack('=L', n)
    return socket.inet_ntoa(s)


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
        ('src', ctypes.c_uint32),
        ('dst', ctypes.c_uint32),
    ]


class IcmpHeader(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('type', ctypes.c_ubyte),
        ('code', ctypes.c_ubyte),
        ('checksum', ctypes.c_uint16),
        #('rest', ctypes.c_uint8*4),
    ]


class EchoHeader(ctypes.Structure):
    _pack_ = 1
    _fields_ = IcmpHeader._fields_ + [
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


def request(identifier=0, sequence=0, data_usecs=0):
    buf = ctypes.create_string_buffer(ctypes.sizeof(EchoHeader))
    icmph = EchoHeader.from_buffer(buf)
    icmph.identifier = identifier
    icmph.sequence = sequence
    icmph.type = 8
    icmph.code = 0
    icmph.data_usecs = data_usecs
    icmph.checksum = inet_checksum(buf[:])
    return buf[:]


def echo_from_ip(s):
    slen = len(s)
    if slen >= ctypes.sizeof(IpAndEchoHeader):
        return IpAndEchoHeader.from_buffer_copy(s[:slen])

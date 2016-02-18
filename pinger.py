
import array
import os
import time

from socket import *
import ctypes


def microsecs():
    return int(time.time() * 1e6)


def inet_checksum(s):
    if len(s) & 1:
        s += '\0'
    n = 0
    for word in array.array('h', s):
        n += (word & 0xffff)
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
        else:
            print pad+name+': '+repr(val)
    if depth == 1:
        print


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


class IcmpHeader(ctypes.BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('type', ctypes.c_ubyte),
        ('code', ctypes.c_ubyte),
        ('checksum', ctypes.c_uint16),
    ]


class EchoHeader(ctypes.BigEndianStructure):
    _pack_ = 1
    _fields_ = IcmpHeader._fields_ + [
        ('identifier', ctypes.c_uint16),
        ('sequence', ctypes.c_uint16),
        ('data_usecs', ctypes.c_uint64),
    ]


class OsxEchoHeader(ctypes.BigEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('ip', IpHeader),
        ('icmp', EchoHeader),
    ]

outbuf = bytearray(ctypes.sizeof(EchoHeader))
icmph = EchoHeader.from_buffer(outbuf)
icmph.type = 8
icmph.code = 0
# icmph.data_usecs = microsecs()
icmph.data_usecs = 0xffffffffffffffff
icmph.checksum = inet_checksum(outbuf)
print [hex(icmph.checksum)]

#print repr(str(outbuf))
#exit()

s = socket(AF_INET, SOCK_DGRAM, IPPROTO_ICMP)
#pop = os.popen('ping -s 16 -p 00 127.0.0.1', 'r')

while 1:
    s.sendto(outbuf, 0, ('127.0.0.1', 0))

    msg = s.recv(512)
    osx_ping = OsxEchoHeader.from_buffer_copy(msg)
    #print ['got msg len', length]
    #dump(ireq)
    #dump(iph)
    dump(osx_ping)
    break


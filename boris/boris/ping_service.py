
from __future__ import absolute_import
import collections
import os
import socket
import random

import twisted.application.service
import twisted.internet.defer
import boris.ipv4
import boris.py


def createIcmpListener(protocol, reactor, ttl=64):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_ICMP)
    s.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
    s.setblocking(False)
    fd = os.dup(s.fileno())
    s.close()
    return reactor.adoptDatagramPort(fd, socket.AF_INET, protocol)


class StatReceiver(object):
    def reply(self, target, sent_usecs, recv_usecs):
        pass


class Receiver(object):
    def on_ping(self, target, sequence, sent_usec, recv_usec):
        pass

    def on_loss(self, target, sent_usec):
        pass

    def on_dup(self, target, sent_usec):
        pass


@boris.py.add_repr(['addr'])
class Target(object):
    def microsecs(self):
        return int(self.reactor.seconds() * 1e6)

    def __init__(self, reactor, protocol, addr, identifier, receiver):
        self.reactor = reactor
        self.protocol = protocol
        self.addr = addr
        self.identifier = identifier
        self.receiver = receiver
        self.sequence = 0
        self.replies = collections.deque()
        self.pending = boris.structures.List()
        self.pending_ts = {}
        self.interval = None
        self.timeout_usec = None
        self.delayedCall = None

    def start(self, interval, timeout_sec=5.0):
        self.interval = interval
        self.timeout_usec = timeout_sec * 1e6
        self._nextInterval()

    def stop(self):
        if self.delayedCall and self.delayedCall.active():
            self.delayedCall.cancel()
        self.interval = None
        self.timeout_usec = None
        self.delayedCall = None

    def _nextInterval(self):
        now = self.microsecs()
        self.expireLost(now)
        self.sendPing(now)
        self.delayedCall = self.reactor.callLater(
            self.interval, self._nextInterval)

    def expireLost(self, now):
        window = now - self.timeout_usec
        while self.pending and self.pending.peekleft() < window:
            lost_ts = self.pending.popleft()
            del self.pending_ts[lost_ts]
            self.receiver.on_loss(self, lost_ts)

    def sendPing(self, now):
        node = self.pending.append(now)
        self.pending_ts[now] = node

        self.sequence += 1
        self.protocol.sendPing(self.addr,
                               self.identifier,
                               self.sequence,
                               now)

    def receivePing(self, icmp):
        now = self.microsecs()
        self.expireLost(now)
        sent = icmp.data_usecs
        window = now - self.timeout_usec

        while self.pending and self.pending.peekleft() < window:
            lost_ts = self.pending.popleft()
            del self.pending_ts[lost_ts]
            self.receiver.on_loss(self, lost_ts)

        node = self.pending_ts.pop(sent, None)
        if not node:
            self.receiver.on_dup(self, sent)
        else:
            self.pending.removenode(node)
            self.receiver.on_ping(self, icmp.sequence, sent, now)


class Protocol(twisted.internet.protocol.DatagramProtocol):
    def __init__(self, reactor, ttl):
        self.reactor = reactor
        self.ttl = ttl
        self._targets = {}

    def addTarget(self, addr, on_receive):
        raw = boris.ipv4.addr_to_int(addr)
        while True:
            identifier = random.randint(0, 0xffff)
            key = (raw, identifier)
            if key not in self._targets:
                target = Target(self.reactor, self, addr, identifier,
                                on_receive)
                self._targets[key] = target
                return target

    def removeTarget(self, target):
        raw = boris.ipv4.addr_to_int(target.addr)
        self._targets.pop((raw, target.identifier), None)

    def sendPing(self, addr, identifier=0, sequence=0, data_usecs=0):
        buf = boris.ipv4.request(identifier, sequence, data_usecs)
        self.transport.write(buf, addr=(addr, 0))

    def go(self):
        self.sendPing(addr='127.0.0.1', data_usecs=microsecs())
        self.transport.reactor.callLater(.1, self.go)

    def datagramReceived(self, msg, _):
        ping = boris.ipv4.echo_from_ip(msg)
        key = (ping.ip.src, ping.icmp.identifier)
        target = self._targets.get(key)
        if target:
            target.receivePing(ping.icmp)


class Service(twisted.application.service.Service):
    TTL = 64

    def __init__(self, reactor):
        self.reactor = reactor
        self.protocol = None
        self.port = None

    def startService(self):
        twisted.application.service.Service.startService(self)
        self.protocol = Protocol(self.reactor, ttl=self.TTL)
        self.port = createIcmpListener(self.protocol,
                                       self.reactor,
                                       ttl=self.TTL)

    def stopService(self):
        twisted.application.service.Service.stopService(self)
        d = twisted.internet.defer.maybeDeferred(self.port.stopListening)
        return d

    def addTarget(self, addr, on_receive):
        return self.protocol.addTarget(addr, on_receive)

    def removeTarget(self, target):
        self.protocol.removeTarget(target)


from __future__ import absolute_import

import twisted.names.client
import twisted.internet.reactor
import boris.ping_service
import boris.structures


class PingReceiver(boris.ping_service.Receiver):
    def on_ping(self, target, sequence, sent_usecs, recv_usecs):
        ms = (recv_usecs - sent_usecs) / 1000.0
        print [target.addr, sequence, '%.2f' % (ms,)]

    def on_loss(self, target, sent_usec):
        print ['loss!', sent_usec]

    def on_dup(self, target, sent_usec):
        print ['dup!', sent_usec]


class App(object):
    def __init__(self, reactor=twisted.internet.reactor):
        self.reactor = reactor
        self.resolver = twisted.names.client.getResolver()
        self.ping_service = boris.ping_service.Service(self.reactor)
        self.targets = []

    ping_targets = [
        '212.58.244.119',
        '8.8.8.8',
        '91.121.165.123',
        '192.168.2.254',
        '217.32.145.130',
    ]

    def startService(self):
        self.ping_service.startService()

        for addr in self.ping_targets:
            target = self.ping_service.addTarget(addr, PingReceiver())
            target.start(0.2)
            self.targets.append(target)

    def run(self):
        self.startService()
        return self.reactor.run()


if __name__ == '__main__':
    app = App()
    app.run()

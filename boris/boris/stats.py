

class RangeStat(object):
    start = None
    end = None
    count = None
    total = None
    low = None
    high = None
    average = None
    samples = None
    lost = None


class RangeStatPublisher(object):
    def on_stat(self, publisher, stat):
        pass


class RangeStatBuilder(object):
    def __init__(self, reactor, name, interval, publisher):
        self.reactor = reactor
        self.name = name
        self.interval = interval
        self.publisher = publisher
        self.stat = None

    def finalize(self):
        if self.stat:
            self.stat.average = self.stat.total / self.stat.count
            self.publisher.on_stat(self, self.stat)
            self.stat = None

    def add(self, value, seconds=None):
        if seconds is None:
            seconds = self.reactor.seconds()

        if self.stat and self.stat.end < seconds:
            self.finalize()

        if self.stat is None:
            self.stat = RangeStat()
            self.stat.start = seconds
            self.stat.end = seconds + interval
            self.stat.count = 1
            self.stat.total = value
            self.stat.low = value
            self.stat.high = value
            self.stat.total += value
            self.stat.count += 1
        else:
            if self.stat.low > value:
                self.stat.low = value
            if self.stat.high < value:
                self.stat.high = value


class ValueStat(object):
    pass




class PublishedValue(object):
    def __init__(self, name, labels):
        self.name = name
        self.labels = labels
        self.listeners = []
        self.last = None

    def listen(self, func):
        self.listeners.append(func)

    def publish(self, value):
        self.last = value
        for func in self.listeners:
            func(self, value)


class Floating(PublishedValue):
    """Floating point value varying over time."""


class Event(PublishedValue):
    """An event optionally occurring at some instant."""


class DataSet(object):
    def __init__(self):
        self.listeners = []
        self.values = []

    def add_pubval(self, pubval):
        labels = set(pubval.labels)
        for labels, func in self.listeners:
            




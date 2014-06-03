
import time


class TokenBucket(object):
    def __init__(self, per_sec, capacity, initial=None):
        self.per_sec = per_sec
        self.capacity = capacity
        self.tokens = initial or capacity
        self.last_fill = time.time()

    def get(self, count=1):
        now = time.time()
        tokens = self.tokens + ((now - self.last_fill) * self.per_sec)
        self.tokens = min(self.capacity or tokens, tokens)
        self.last_fill = now
        if count <= self.tokens:
            self.tokens -= count
            return count
        return 0

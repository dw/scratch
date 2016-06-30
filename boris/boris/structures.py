


_undefined = object()


class ListNode(object):
    left = None
    right = None
    data = None


class List(object):
    def __init__(self):
        self.first = None
        self.last = None
        self.length = 0

    def __len__(self):
        return self.length

    def peekleft(self):
        if self.first:
            return self.first.data

    def peekright(self):
        if self.last:
            return self.last.data

    def appendleft(self, data):
        node = ListNode()
        node.data = data
        node.right = self.first
        if self.first:
            self.first.left = node
            self.first = node
        else:
            self.first = node
            self.last = node
        self.length += 1

    def append(self, data):
        node = ListNode()
        node.data = data
        node.left = self.last
        if self.last:
            self.last.right = node
            self.last = node
        else:
            self.first = node
            self.last = node
        self.length += 1
        return node

    def removenode(self, node):
        if node.left:
            node.left.right = node.right
        else:
            self.first = node.right

        if node.right:
            node.right.left = node.left
        else:
            self.last = node.left

        node.left = _undefined
        node.right = _undefined
        self.length -= 1

    def pop(self):
        if not self.last:
            raise IndexError()

        node = self.last
        self.last = node.left
        if self.last:
            self.last.right = None
        else:
            self.first = None

        node.left = _undefined
        node.right = _undefined
        self.length -= 1
        return node.data

    def popleft(self):
        if not self.first:
            raise IndexError()

        node = self.first
        self.first = node.right
        if self.first:
            self.first.left = None
        else:
            self.last = None

        node.left = _undefined
        node.right = _undefined
        self.length -= 1
        return node.data


class RingBuffer(object):
    def __init__(self, size):
        self.data = [None]*size
        self.put_idx = 0
        self.get_idx = 0

    def get(self):
        if self.get_idx != self.put_idx:
            idx = (self.get_idx + 1) % len(self.data)
            self.get_idx = idx
            return self.data[idx]

    def peek(self):
        if self.get_idx != self.put_idx:
            idx = (self.get_idx + 1) % len(self.data)
            return self.data[idx]

    def put(self, val):
        idx = self.put_idx
        self.put_idx = (idx + 1) % len(self.data)
        self.data[idx] = val
        get_idx = self.get_idx
        if get_idx == idx:
            print 'overflow'
            self.get_idx = (get_idx + 1) % len(self.data)

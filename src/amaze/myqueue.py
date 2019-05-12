class Queue:

    def __init__(self):
        self.v = ["dummy", "dummy"]
        self.len = 2
        self.items = 0
        self.head = 0
        self.tail = 0

    def empty(self):
        return self.items == 0

    def increase_queue(self):
        self.v = self.v + self.v
        if self.head < self.tail:
            self.tail += self.len
        self.len = self.len * 2

    def append(self, item):
        if self.len-1 == self.items:
            self.increase_queue()
        self.v[self.head] = item
        self.head += 1
        if self.head == self.len:
            self.head = 0
        self.items = self.items+1

    def pop(self):
        x = self.v[self.tail]
        self.tail += 1
        if self.tail == self.len:
            self.tail = 0
        self.items = self.items-1
        return x

    def push(self, item):
        if self.len-1 == self.items:
            self.increase_queue()
        self.v[self.tail] = item
        self.tail -= 1
        if self.tail < 0:
            self.tail = self.len - 1
        self.items = self.items+1

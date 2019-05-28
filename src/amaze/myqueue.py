class Queue:

    def __init__(self):
        self.len = 200
        self.v = ["d" for x in range(self.len)]
        self.items = 0
        self.head = 0
        self.tail = 0

    def fromBuffer(self, buffer):
        self.v = buffer

    def empty(self):
        return self.items == 0

    def chunks(self, n):
        self.trim()
        for i in range(0, len(l), n):
            yield self.fromBuffer(self.v[i:i + n])

    def trim(self):
        if (head < tail):
            self.v = self.v[self.tail:self.head+1]
        else:
            self.v = self.v[self.tail:] + self.v[:self.head+1]
        self.tail = 0
        self.head = len(self.v)
        self.len = len(self.v)
        self.items = self.len-1

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


class PriorityQueue:
    def __init__(self):
        self.queue = {}
        self.items = []

    def empty(self):
        return len(self.queue) == 0

    def pop(self):
        for queue in self.items:
            item = queue[1].pop()
            if queue[1].empty():
                self.queue.pop(queue[0])
                self.items = sorted(self.queue.items())
            return item
        return None

    def append(self, item):
        if item.depth in self.queue:
            q = self.queue[item.depth]
        else:
            q = Queue()
            self.queue[item.depth] = q
            self.items = sorted(self.queue.items())
        q.append(item)


class PriorityStack:
    def __init__(self):
        self.stack_dict = dict()
        self.sorted_keys = []

    def calc_sorted_keys(self):
        self.sorted_keys = list(self.stack_dict.keys())
        self.sorted_keys.sort()

    def empty(self):
        return len(self.sorted_keys) == 0

    def pop(self):
        stack = self.stack_dict[self.sorted_keys[0]]
        ret = stack.pop()
        if len(stack) == 0:
            self.stack_dict.pop(self.sorted_keys[0])
            self.calc_sorted_keys()
        return ret

    def append(self, key, item):
        if key in self.stack_dict:
            stack = self.stack_dict[key]
        else:
            stack = []
            self.stack_dict[key] = stack
            self.calc_sorted_keys()
        stack.append(item)

    def size(self):
        c = 0
        for x in self.stack_dict.items():
            c += len(x[1])
        return c



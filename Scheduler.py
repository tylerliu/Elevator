class Scheduler:

    def next_floor(self, requests, full):
        return 0

class MinMaxScheduler(Scheduler):

    def __init__(self):
        self.current = 0

    def next_floor(self, requests, full):
        if self.current == 0:
            for i in reversed(range(len(requests))):
                if requests[i]:
                    self.current = i
                    break
        else:
            while self.current > 0:
                self.current -= 1
                if requests[self.current]:
                    break
        return self.current

class ExpressScheduler(Scheduler):
    def __init__(self):
        self.current = 0
        self.next = 0

    def next_floor(self, requests, full):
        if self.current != 0:
            self.current = 0
            return 0
        self.current = self.next + 1
        self.next = (self.next + 1) % (len(requests) - 1)
        return self.current


class ReverseExpressScheduler(Scheduler):
    def __init__(self):
        self.current = 0
        self.next = 0

    def next_floor(self, requests, full):
        if self.current != 0:
            self.current = 0
            return 0
        self.current = self.next + 1 if self.next + 1 < len(requests) else ((len(requests) - 1) * 2) - self.next
        self.next = (self.next + 1) % ((len(requests) - 1) * 2)
        return self.current
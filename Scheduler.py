class Scheduler:

    def next_floor(self, up_requests, down_requests, full):
        return 0

    def going_up(self):
        return False

class MinMaxScheduler(Scheduler):

    def __init__(self):
        self.current = 0
        self.goingUp = True

    def get_next_up(self, up_requests):
        start_floor = self.current + 1 if self.goingUp else 0
        up_requests = up_requests[start_floor:]
        for i, r in enumerate(up_requests):
            if r:
                return start_floor + i
        return None

    def get_next_down(self, down_requests):
        start_floor = self.current if not self.goingUp else len(down_requests)
        down_requests = down_requests[:start_floor]
        for i in reversed(range(len(down_requests))):
            if down_requests[i]:
                return i
        return None

    def next_floor(self, up_requests, down_requests, full):
        if self.goingUp:
            nex = self.get_next_up(up_requests)
            if nex is not None:
                self.current = nex
            else:
                self.current = self.get_next_down(down_requests)
                if self.current is None: self.current = 0
                self.goingUp = False
        else: # going down
            nex = self.get_next_down(down_requests)
            if nex is not None:
                self.current = nex
            else:
                if full != 0:
                    self.current = 0
                else:
                    self.current = self.get_next_up(up_requests)
                    if self.current is None: self.current = 0
                self.goingUp = True

        return self.current

    def going_up(self):
        return self.goingUp

class ExpressScheduler(Scheduler):
    def __init__(self):
        self.current = 0
        self.next = 0

    def next_floor(self, up_requests, down_requests, full):
        if self.current != 0:
            self.current = 0
            return 0
        self.current = self.next + 1
        self.next = (self.next + 1) % (len(down_requests) - 1)
        return self.current

    def going_up(self):
        return self.current == 0


class DynamicExpressScheduler(Scheduler):
    def __init__(self):
        self.current = 0
        self.next = 0

    def next_floor(self, up_requests, down_requests, full):
        if (self.current != 0 and full > 0.99) or (self.current == len(down_requests) - 1 and full > 0.01):
            self.current = 0
            return 0
        self.current = self.next + 1
        self.next = (self.next + 1) % (len(down_requests) - 1)
        if full > 0.001 and self.current == 1:
            self.current = 0
        return self.current

    def going_up(self):
        return self.current == 0


class ReverseExpressScheduler(Scheduler):
    def __init__(self):
        self.current = 0
        self.next = 0

    def next_floor(self, up_requests, down_requests, full):
        if self.current != 0:
            self.current = 0
            return 0
        self.current = self.next + 1 if self.next + 1 < len(down_requests) else ((len(down_requests) - 1) * 2) - self.next
        self.next = (self.next + 1) % ((len(down_requests) - 1) * 2)
        return self.current

    def going_up(self):
        return self.current == 0

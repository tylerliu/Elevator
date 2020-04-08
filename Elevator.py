from queue import PriorityQueue
from numpy import random
from Scheduler import *
from collections.abc import Iterable

class ElevatorQueue():
    def __init__(self, floors, initial_count = 0, pressing_up = 'none'):
        self.waits = [PriorityQueue() for _ in range(floors)]
        for i in self.waits[1:]:
            for _ in range(initial_count): i.put(0)
        self.up_request = [False for _ in range(floors)]
        self.down_request = [False for _ in range(floors)]
        self.pressing_up = pressing_up
        if pressing_up != 'none' and pressing_up != 'always' and pressing_up != 'when_full':
            raise ValueError

    def get_down_request(self):
        for i in range(len(self.down_request)):
            self.down_request[i] = self.down_request[i] or (not self.waits[i].empty())
        return self.down_request

    def get_up_request(self):
        if self.pressing_up == 'always':
            for i in range(len(self.up_request)):
                self.up_request[i] = self.up_request[i] or (not self.waits[i].empty())
        return self.up_request

    def request_count(self):
        return list(map(lambda f: f.qsize(), self.waits))

    def pop_request(self, floor):
        return self.waits[floor].get_nowait() if not self.waits[floor].empty() else -1

    def add_request(self, time, floor):
        self.waits[floor].put(time)

    # p: chance of changing per second in all floors
    def waiting(self, time, p):
            p2 = (p[t - time] if isinstance(p, Iterable) else p) / len(self.waits)
            result = random.choice([True, False], len(self.waits) - 1, replace=True, p = [p2, 1-p2])
            for f, adding in zip(self.waits[1:], result):
                if adding:
                    f.put(time)

    def print_debug(self):
        print("Longest_queues: " + str(max(map(lambda f: f.qsize(), self.waits))))

    def get_stats(self):
        return {"Longest_queue": max(map(lambda f: f.qsize(), self.waits))}

    def arrives_at(self, floor, going_up, full):
        if going_up:
            self.up_request[floor] = False
        else:
            self.down_request[floor] = False
        if self.pressing_up == 'when_full' and full == True and self.waits[floor].qsize() > 0:
            self.up_request[floor] = True

class PassengerLogger():

    def __init__(self, capacity, elevator):
        self.capacity = capacity
        self.arrived_count = 0
        self.total_wait = 0
        self.passengers = []
        self.elevator = elevator

    def load_passenger(self, queue : ElevatorQueue, floor):
        if len(self.passengers) == self.capacity: return False
        passenger = queue.pop_request(floor)
        if passenger != -1:
            self.passengers.append(passenger)
        return passenger != -1

    def unload_passenger(self, time):
        if len(self.passengers) != 0:
            self.arrived_count += 1
            self.total_wait += time - self.passengers.pop()
        return self.passengers != 0

    def fullness(self):
        return len(self.passengers) / self.capacity

    def is_ready(self, queue, floor):
        if floor == 0:
            return len(self.passengers) == 0
        if len(self.passengers) == self.capacity or queue.request_count()[floor] == 0:
            return True

    def print_debug(self, time, queue : ElevatorQueue):
        print("Elevator has", len(self.passengers), "Carts")
        print("%d out of %d arrived, throughput %f / hr" % (self.arrived_count, self.arrived_count + sum(queue.request_count()), self.arrived_count / time * 3600 if time != 0 else float('nan')))
        print("Turnaround time %f s" %(self.total_wait / self.arrived_count if self.arrived_count != 0 else 0))

    def get_string(self, time):
        string = "Throughput %d / hr in %d seconds" % (self.arrived_count / time * 3600 if time != 0 else float('nan'), time)
        string += "\nTurnaround time %d s for %d arrived carts" % (self.total_wait / self.arrived_count if self.arrived_count != 0 else 0, self.arrived_count)
        return string

    def get_stats(self, time, queue: ElevatorQueue):
        return {"Throughput": self.arrived_count / time * 3600 if time != 0 else float('nan'),
                "Turnaround": self.total_wait / self.arrived_count if self.arrived_count != 0 else 0,
                "Total_Load": self.arrived_count + sum(queue.request_count())}

    def reset_stat(self):
        self.arrived_count = 0
        self.total_wait = 0

class Elevator:
    LOADING_TIME = 4
    START_STOP_TIME = 4

    def __init__(self, scheduler, floors, p, capacity, initial_count = 0, pressing_up = 'none'):
        self.queue = ElevatorQueue(floors, initial_count, pressing_up=pressing_up)
        self.scheduler = scheduler
        self.p = p
        self.time = 0
        self.step_left, self.step_from, self.step_to = 0, 0, 0
        self.passengerLogger = PassengerLogger(capacity, self)


    def tick(self):
        self.queue.waiting(self.time, self.p)
        if self.step_left != 0:
            self.step_left -= 1
        else: # next step
            if self.step_from == self.step_to:
                if self.step_to == 0:
                    self.passengerLogger.unload_passenger(self.time)
                else :
                    self.passengerLogger.load_passenger(self.queue, self.step_to)
            else:
                self.queue.arrives_at(self.step_to, self.scheduler.going_up(), self.passengerLogger.fullness() > 0.999)

            self.step_from = self.step_to
            if self.passengerLogger.is_ready(self.queue, self.step_from):
                self.step_to = self.scheduler.next_floor(self.queue.get_up_request(), self.queue.get_down_request(), self.passengerLogger.fullness())
                self.step_left = self.step_time(self.step_from, self.step_to)
            else:
                self.step_to = self.step_from
                self.step_left = Elevator.LOADING_TIME

        # self.print_debug()
        self.time += 1

    def add_request(self, floor):
        self.queue.add_request(self.time, floor)


    def print_debug(self):
        print("Time: ", self.time)
        self.passengerLogger.print_debug(self.time, self.queue)
        print("Elevator going from %d to %d, arrive in %d seconds" % (self.step_from, self.step_to, self.step_left))
        self.queue.print_debug()

    def __str__(self):
        return self.passengerLogger.get_string(self.time)

    @staticmethod
    def step_time(floor_from, floor_to):
        if floor_from == floor_to: return 1
        return int(2 * Elevator.START_STOP_TIME + 2.25 * abs(floor_to - floor_from))

    def calc_location(self):
        if self.step_from == self.step_to:
            return self.step_to
        ans = (self.step_left - Elevator.START_STOP_TIME) / \
                (self.step_time(self.step_from, self.step_to) - 2 * Elevator.START_STOP_TIME)
        return min(max(ans, 0), 1)

    def get_stat(self):
        stats = self.queue.get_stats()
        stats.update(self.passengerLogger.get_stats(self.time, self.queue))
        return stats

    def reset_stat(self):
        self.time = 0
        self.passengerLogger.reset_stat()


if __name__ == '__main__':
    elevator = Elevator(scheduler=ExpressScheduler(), floors=7, p =0.4/10, capacity=2, initial_count=0)
    for t in range(7200):
        elevator.tick()
    elevator.print_debug()
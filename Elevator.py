from queue import PriorityQueue
from numpy import random
from Scheduler import *

class ElevatorQueue():
    def __init__(self, floors, initial_count = 0):
        self.waits = [PriorityQueue() for _ in range(floors)]
        for i in self.waits[1:]:
            for _ in range(initial_count): i.put(0)

    def get_request(self):
        return [not f.empty() for f in self.waits]

    def pop_request(self, floor):
        return self.waits[floor].get_nowait() if not self.waits[floor].empty() else -1

    # p: chance of changing per second in all floors
    def waiting(self, time, p):
            p2 = (p if isinstance(p, float) else p[t - time]) / len(self.waits)
            result = random.choice([True, False], len(self.waits) - 1, replace=True, p = [p2, 1-p2])
            for f, adding in zip(self.waits[1:], result):
                if adding:
                    f.put(time)

    def print_debug(self):
        print("Requests: " + " ".join(map(lambda f: str(f.qsize()), self.waits)))

class PassengerLogger():

    def __init__(self, capacity):
        self.capacity = capacity
        self.arrived_count = 0
        self.total_wait = 0
        self.passengers = []

    def load_passenger(self, queue : ElevatorQueue, floor):
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
        if len(self.passengers) == self.capacity or queue.get_request()[floor] == False:
            return True

    def print_debug(self, time):
        print("Elevator has", len(self.passengers), "Carts")
        print("%d arrived, throughput %f / hr" % (self.arrived_count, self.arrived_count / time * 3600 if time != 0 else float('nan')))
        print("Total wait %d s, Turnaround time %f s" %(self.total_wait, self.total_wait / self.arrived_count if self.arrived_count != 0 else float('nan')))



class Elevator:
    LOADING_TIME = 2

    def __init__(self, scheduler, floors, p, capacity, initial_count = 0):
        self.queue = ElevatorQueue(floors, initial_count)
        self.scheduler = scheduler
        self.p = p
        self.time = 0
        self.step_left, self.step_from, self.step_to = 0, 0, 0
        self.passengerLogger = PassengerLogger(capacity)


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

            self.step_from = self.step_to
            if self.passengerLogger.is_ready(self.queue, self.step_from):
                self.step_to = self.scheduler.next_floor(self.queue.get_request(), self.passengerLogger.fullness())
                self.step_left = self.step_time(self.step_from, self.step_to)
            else:
                self.step_to = self.step_from
                self.step_left = Elevator.LOADING_TIME

        self.print_debug()
        self.time += 1


    def print_debug(self):
        print("Time: ", self.time)
        self.passengerLogger.print_debug(self.time)
        print("Elevator going from %d to %d, arrive in %d seconds" % (self.step_from, self.step_to, self.step_left))
        self.queue.print_debug()


    @staticmethod
    def step_time(floor_from, floor_to):
        if floor_from == floor_to: return 0
        return int(3 + 8 + 2.25 * abs(floor_to - floor_from))


if __name__ == '__main__':
    elevator = Elevator(scheduler=RRScheduler(), floors=7, p = 1 / 20, capacity=2, initial_count= 10)
    for t in range(3600):
        elevator.tick()
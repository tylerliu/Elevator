from matplotlib import pyplot as plt

from Elevator import Elevator
from Scheduler import ExpressScheduler, MinMaxScheduler
from tqdm import tqdm

def simulate(elevator):
    for _ in range(14400):
        elevator.tick()
    stat1 = elevator.get_stat()
    elevator.p = 0
    while elevator.passengerLogger.fullness() != 0 or sum(elevator.queue.request_count()) != 0:
        elevator.tick()
    stat1['Turnaround'] = elevator.get_stat()['Turnaround']
    return stat1


def elevator_to_stat(stats, **elevator_args):
    stat_list = []
    for _ in range(4):
        stat_list.append(simulate(Elevator(**elevator_args)))
    for k in stats.keys():
        l = sum([stat[k] for stat in stat_list]) / len(stat_list)
        stats[k].append(l)


def plot_metric(metric, units, name=None, log=False):
    if name is None:
        name = metric
    plt.plot(x, y_express[metric], label="Express Scheduling")
    plt.plot(x, y_minmax[metric], label="Normal Scheduling")
    plt.plot(x, y_minmax_cheat[metric], label="Normal Scheduling with Pressed up")
    plt.legend()
    plt.title('%s vs Load' % name)
    plt.xlabel('Business(carts / 10s)')
    plt.ylabel('%s(%s)' % (name, units))
    if log:
        plt.yscale('log')
    plt.show()

if __name__ == '__main__':
    x = range(101)
    y_express = {'Longest_queue': [], 'Throughput': [], 'Turnaround': []}
    y_minmax = {'Longest_queue': [], 'Throughput': [], 'Turnaround': []}
    y_minmax_cheat = {'Longest_queue': [], 'Throughput': [], 'Turnaround': []}
    for business in tqdm(range(101)):
        elevator_to_stat(y_express, scheduler=ExpressScheduler(),
                         floors=7, p=business / 100 / 10, capacity=2, initial_count=0)
        elevator_to_stat(y_minmax, scheduler=MinMaxScheduler(),
                         floors=7, p=business / 100 / 10, capacity=2, initial_count=0)
        elevator_to_stat(y_minmax_cheat, scheduler=MinMaxScheduler(),
                         floors=7, p=business / 100 / 10, capacity=2, initial_count=0, pressing_up=True)

    plot_metric('Throughput', 'carts / hr')
    plot_metric('Longest_queue', 'carts', name='Longest Queue')
    plot_metric('Turnaround', 's', name='Turnaround Time', log=True)

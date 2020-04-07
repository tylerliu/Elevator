from matplotlib import pyplot as plt

from Elevator import Elevator
from Scheduler import ExpressScheduler, MinMaxScheduler, DynamicExpressScheduler
from tqdm import tqdm
import numpy as np

SIM_HOURS = 4

def simulate(elevator):
    for _ in range(SIM_HOURS * 3600):
        elevator.tick()
    stat1 = elevator.get_stat()
    elevator.p = 0
    while elevator.passengerLogger.fullness() != 0 or sum(elevator.queue.request_count()) != 0:
        elevator.tick()
    stat1['Turnaround'] = elevator.get_stat()['Turnaround'] / 60  # in minutes
    stat1["Total_Load"] = stat1["Total_Load"] / SIM_HOURS
    return stat1


def elevator_to_stat(stats, **elevator_args):
    for _ in range(1):
        stat = simulate(Elevator(**elevator_args))
        for k in stats.keys():
            stats[k].append(stat[k])


def plot_metric(metric, units, name=None, log=False):
    if name is None:
        name = metric
    plt.plot(y_express["Total_Load"], y_express[metric], label="Express Scheduling")
    plt.plot(y_minmax["Total_Load"], y_minmax[metric], label="Normal Scheduling")
    plt.plot(y_minmax_always["Total_Load"], y_minmax_always[metric], label="Normal Scheduling with Pressed up")
    plt.legend()
    plt.title('%s vs Load' % name)
    plt.xlabel('Load(carts / 1hr)')
    plt.ylabel('%s(%s)' % (name, units))
    if log:
        plt.yscale('log')
    plt.show()

def pack_and_sort(metrics):
    for k in metrics:
        metrics[k] = np.array(metrics[k])
    sort_key = np.argsort(metrics["Total_Load"])
    for k in metrics:
        metrics[k] = metrics[k][sort_key]

if __name__ == '__main__':
    y_dynamic_express = {'Longest_queue': [], 'Throughput': [], 'Turnaround': [], "Total_Load": []}
    y_express = {'Longest_queue': [], 'Throughput': [], 'Turnaround': [], "Total_Load": []}
    y_minmax = {'Longest_queue': [], 'Throughput': [], 'Turnaround': [], "Total_Load": []}
    y_minmax_always = {'Longest_queue': [], 'Throughput': [], 'Turnaround': [], "Total_Load": []}
    y_minmax_full = {'Longest_queue': [], 'Throughput': [], 'Turnaround': [], "Total_Load": []}

    for business in tqdm(range(101)):
        elevator_to_stat(y_dynamic_express, scheduler=DynamicExpressScheduler(),
                         floors=7, p=business / 100 / 10, capacity=2, initial_count=0)
        elevator_to_stat(y_express, scheduler=ExpressScheduler(),
                         floors=7, p=business / 100 / 10, capacity=2, initial_count=0)
        elevator_to_stat(y_minmax, scheduler=MinMaxScheduler(),
                         floors=7, p=business / 100 / 10, capacity=2, initial_count=0)
        elevator_to_stat(y_minmax_always, scheduler=MinMaxScheduler(),
                         floors=7, p=business / 100 / 10, capacity=2, initial_count=0, pressing_up='always')
        elevator_to_stat(y_minmax_full, scheduler=MinMaxScheduler(),
                         floors=7, p=business / 100 / 10, capacity=2, initial_count=0, pressing_up='when_full')

    pack_and_sort(y_express)
    pack_and_sort(y_minmax)
    pack_and_sort(y_minmax_always)

    plot_metric('Throughput', 'carts / hr')
    plot_metric('Longest_queue', 'carts', name='Longest Queue')
    plot_metric('Turnaround', 's', name='Turnaround Time', log=True)

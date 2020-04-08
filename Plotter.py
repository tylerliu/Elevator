from matplotlib import pyplot as plt

from Elevator import Elevator
from Scheduler import ExpressScheduler, MinMaxScheduler, DynamicExpressScheduler
import numpy as np
from multiprocessing import Pool

SIM_HOURS = 4
NUM_REPEAT = 4

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


def get_sets(elevator_args):
    return simulate(Elevator(**elevator_args))

def to_stats(list_of_stat):
    stats = {k : [] for k in list_of_stat[0]}
    for k in stats:
        for l in list_of_stat:
            stats[k].append(l[k])

    return stats


def plot_metric(metric, units, name=None, log=False):
    if name is None:
        name = metric
    plt.plot(y_dynamic_express["Total_Load"], y_dynamic_express[metric], label="Dynamic Express Scheduling")
    plt.plot(y_express["Total_Load"], y_express[metric], label="Express Scheduling")
    plt.plot(y_minmax["Total_Load"], y_minmax[metric], label="Normal Scheduling")
    plt.plot(y_minmax_always["Total_Load"], y_minmax_always[metric], label="Normal Scheduling with always Pressed up")
    plt.plot(y_minmax_full["Total_Load"], y_minmax_full[metric], label="Normal Scheduling with Pressed up when full")
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
    pool = Pool()

    dy_list = pool.map(get_sets, [{'scheduler': DynamicExpressScheduler(),
                         'floors': 7, 'p': business / 1000, 'capacity': 2, 'initial_count': 0}
                            for business in range(101)] * NUM_REPEAT)
    y_dynamic_express = to_stats(dy_list)
    print('dynamic_express done')

    e_list = pool.map(get_sets, [{'scheduler': ExpressScheduler(),
                         'floors': 7, 'p': business / 1000, 'capacity': 2, 'initial_count': 0}
                                  for business in range(101)] * NUM_REPEAT)
    y_express = to_stats(e_list)
    print('express done')

    mm_list = pool.map(get_sets, [{'scheduler': MinMaxScheduler(),
                                  'floors': 7, 'p': business / 1000, 'capacity': 2, 'initial_count': 0}
                                 for business in range(101)] * NUM_REPEAT)
    y_minmax = to_stats(mm_list)
    print('minmax done')

    mma_list = pool.map(get_sets, [{'scheduler': MinMaxScheduler(),
                                   'floors': 7, 'p': business / 1000, 'capacity': 2, 'initial_count': 0,
                                    'pressing_up': 'always'}
                                  for business in range(101)] * NUM_REPEAT)
    y_minmax_always = to_stats(mma_list)
    print('minmax always done')

    mmf_list = pool.map(get_sets, [{'scheduler': MinMaxScheduler(),
                                   'floors': 7, 'p': business / 1000, 'capacity': 2, 'initial_count': 0,
                                    'pressing_up': 'when_full'}
                                   for business in range(101)] * NUM_REPEAT)
    y_minmax_full = to_stats(mmf_list)
    print('minmax full done')

    pool.close()
    pool.join()

    pack_and_sort(y_dynamic_express)
    pack_and_sort(y_express)
    pack_and_sort(y_minmax)
    pack_and_sort(y_minmax_always)
    pack_and_sort(y_minmax_full)

    plot_metric('Throughput', 'carts / hour')
    plot_metric('Longest_queue', 'carts', name='Longest Queue')
    plot_metric('Turnaround', 'minutes', name='Turnaround Time', log=True)

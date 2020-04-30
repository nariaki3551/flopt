import pickle
from argparse import ArgumentParser

import flopt
from flopt import Solver_list
from flopt.performance import Dataset_list
from flopt.performance import performance


def view_performance(algos, dataset_names, xitem):
    """
    display the log (dataset, algo).
    log data is laod from ./performance/algo/dataset/instance/log.pickle

    Parameters
    ----------
    algos : list of str
      algorithm name
    dataset_names : list of str
      dataset names
    xitem : str
      x-label item of fiture. 'time' or 'iteration'
    """
    datasets = [
        flopt.performance.datasets[dataset_name]
        for dataset_name in dataset_names
    ]

    flopt.performance.performance(
        datasets,
        algos,
        xitem=xitem
    )


def argparser():
    parser = ArgumentParser()
    parser.add_argument(
        '--algo',
        nargs='*',
        default=['all'],
        choices=Solver_list()+['all'],
    )
    parser.add_argument(
        '--datasets',
        nargs='*',
        default=['all'],
        choices=Dataset_list()+['all']
    )
    parser.add_argument(
        '--xitem',
        default='time',
        choices=['time', 'iteration']
    )
    return parser


if __name__ == '__main__':
    parser = argparser()
    args = parser.parse_args()

    algos    = args.algo
    datasets = args.datasets
    xitem    = args.xitem

    if algos == ['all']:
        algos = Solver_list()
    if datasets == ['all']:
        datasets = Dataset_list()
    print(algos, datasets)

    view_performance(algos, datasets, xitem)

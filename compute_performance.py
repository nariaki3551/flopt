import os
import pickle
from argparse import ArgumentParser
from itertools import product

import flopt
from flopt import Solver, Solver_list
from flopt.performance import Dataset_list

def compute(algo, dataset_names, params):
    """
    compute the peformance of (dataset, algo).
    log data is saved ./performance/algo/dataset/instance/log.pickle

    Parameters
    ----------
    algo : str
      algorithm name
    dataset_names : list of str
      dataset names
    params : dict
      parameters
    """
    solver = Solver(algo=algo)
    solver.setParams(params=params)

    datasets = [
        flopt.performance.datasets[dataset_name]
        for dataset_name in dataset_names
    ]

    flopt.performance.compute(datasets, solver, msg=True)


def read_paramfile(paramfile):
    params = dict()
    if paramfile is None:
        return params
    for line in open(paramfile, 'r'):
        line = line.strip()
        if line:
            param_name, param_value = line.split('=')
            param_name  = param_name.strip()
            param_value = param_value.strip()
            if param_value in {'infty', 'unlimited', "float('inf')", 'float("inf")'}:
                param_value = float('inf')
            else:
                param_value = float(param_value)
            params[param_name] = param_value
    return params


def argparser():
    print(Solver_list, Dataset_list)
    parser = ArgumentParser()
    parser.add_argument(
        'algorithm',
        choices=Solver_list(),
    )
    parser.add_argument(
        'savename',
    )
    parser.add_argument(
        '--datasets',
        nargs='*',
        choices=Dataset_list(),
        help='instance dataset'
    )
    parser.add_argument(
        '--params',
        default=None,
        help='param file'
    )
    return parser


if __name__ == '__main__':
    parser = argparser()
    args = parser.parse_args()

    algo      = args.algorithm
    savename  = args.savename
    datasets  = args.datasets
    paramfile = args.params

    params = read_paramfile(paramfile)
    params['name'] = savename

    compute(algo, datasets, params)

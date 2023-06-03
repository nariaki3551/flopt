import random
from argparse import ArgumentParser

import flopt
from flopt import Solver, Solver_list
from flopt.performance import Dataset_list
from flopt.env import setup_logger


logger = setup_logger(__name__)


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
    assert "timelimit" in params
    solver = Solver(algo=algo)

    datasets = [
        flopt.performance.get_dataset(dataset_name) for dataset_name in dataset_names
    ]

    flopt.performance.compute(datasets, solver, msg=True, **params)


def setLogger(log_level):
    flopt.env.setLogLevel(log_level)


def argparser():
    parser = ArgumentParser()
    parser.add_argument(
        "algorithm",
        choices=Solver_list(),
    )
    parser.add_argument(
        "savename",
    )
    parser.add_argument(
        "--datasets", nargs="*", choices=Dataset_list(), help="instance dataset"
    )
    parser.add_argument(
        "--timelimit", default=60, type=float, help="timelimit for each instance"
    )
    parser.add_argument(
        "--log_level",
        type=int,
        default=30,
        help="10:DEBUG,20:INFO,30:WARNING,40:ERROR,50:CRITICAL",
    )
    return parser


if __name__ == "__main__":
    parser = argparser()
    args = parser.parse_args()

    algo = args.algorithm
    savename = args.savename
    datasets = args.datasets
    log_level = args.log_level

    params = {"timelimit": args.timelimit}

    compute(algo, datasets, params)

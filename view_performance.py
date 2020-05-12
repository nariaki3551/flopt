import pickle
from argparse import ArgumentParser

import flopt
from flopt import Solver_list
from flopt.performance import Dataset_list
from flopt.performance import performance


def view_performance(algos, dataset_names,
    xitem, yscale, plot_type, save_prefix):
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
    yscale : str
        linear or log
    plot_type : str
        'all' or 'each'
    save_prefix : str
        save figure {save_prefix}instance_name.pdf
    """
    datasets = [
        flopt.performance.datasets[dataset_name]
        for dataset_name in dataset_names
    ]

    flopt.performance.performance(
        datasets,
        algos,
        xitem=xitem,
        yscale=yscale,
        plot_type=plot_type,
        save_prefix=save_prefix
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
        '--dataset',
        nargs='*',
        default=['all'],
        choices=Dataset_list()+['all']
    )
    parser.add_argument(
        '--xitem',
        default='time',
        choices=['time', 'iteration']
    )
    parser.add_argument(
        '--yscale',
        default='linear',
        choices=['linear', 'log']
    )
    parser.add_argument(
        '--plot_type',
        default='all',
        choices=['all', 'each', 'noshow']
    )
    parser.add_argument(
        '--save_prefix',
        default=None
    )
    parser.add_argument(
        '--log_level',
        type=int,
        default=30,
        help='10:DEBUG,20:INFO,30:WARNING,40:ERROR,50:CRITICAL'
    )
    return parser


if __name__ == '__main__':
    parser = argparser()
    args = parser.parse_args()

    algos       = args.algo
    dataset     = args.dataset
    xitem       = args.xitem
    yscale      = args.yscale
    plot_type   = args.plot_type
    save_prefix = args.save_prefix
    log_level   = args.log_level

    flopt.env.setLogLevel(log_level)

    if algos == ['all']:
        algos = Solver_list()
    if dataset == ['all']:
        dataset = Dataset_list()

    view_performance(
        algos, dataset, xitem, yscale,
        plot_type, save_prefix
    )

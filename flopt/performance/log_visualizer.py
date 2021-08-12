import os
import pickle
from math import ceil
from glob import glob
from itertools import product
from collections import defaultdict

import numpy as np

from flopt import env as flopt_env
from flopt.solvers.solver_utils.common import value2str
from flopt.env import setup_logger

performance_dir = flopt_env.performance_dir
logger = setup_logger(__name__)


class LogVisualizer:
    """
    Log visualizer from logs.

    We input logs by constructor or loading from performance directory.

    Parameters
    ----------
    logs : dict
      logs[dataset, instance, solver_name] = log

    Examples
    --------

    .. code-block:: python

      log_visualizer = LogVisualiser()
      log_visualizer.load(
          solver_names=['RandomSearch', '2-Opt'],
          datasets=['tsp']
      )
      log_visualizer.plot()
    """
    def __init__(self, logs=dict()):
        self.logs = logs


    def load(self, solver_names, datasets, load_prefix=performance_dir):
        if isinstance(solver_names, str):
            solver_names = [solver_names]
        if isinstance(datasets, str):
            datasets = [datasets]
        for solver_name, dataset in product(solver_names, datasets):
            self.load_log(solver_name, dataset, load_prefix)


    def load_log(self, solver_name, dataset, load_prefix=performance_dir):
        """
        load log pickle file from load_prefix/solver_name/dataset/instance/log.pickle

        Parameters
        ----------
        solver_name : str
          solver name
        dataset : str
          dataset name
        load_prefix : str
          log saved path
        """
        for picklefile in glob(f'{load_prefix}/{solver_name}/{dataset}/*/log.pickle'):
            instance_name = picklefile.split('/')[-2]
            with open(picklefile, 'rb') as pf:
                self.logs[dataset, instance_name, solver_name] = pickle.load(pf)


    def plot(self, xitem='time', yscale='linear',
            plot_type='all', save_prefix=None, col=2):
        """
        plot all logs

        Parameters
        ----------
        xitem : str
            x-label name. 'time' or 'iteration'
        yscale : str
            linear or log
        plot_type : str
            all: create figures for each dataset.
            each: create figures for each instance.
            noshow: do not create figures.
        col : int
            #columns of figure
        """
        import matplotlib.pyplot as plt
        datasets = set(dataset for dataset, _, _ in self.logs)
        for dataset in datasets:
            instances = set(i for d, i, _ in self.logs if d == dataset)
            n_instance = len(instances)
            col = 1 if n_instance < 2 else col
            row = ceil(n_instance/col)
            if plot_type == 'all':
                fig, axs = plt.subplots(row, col)
                fig.suptitle(dataset)
                if n_instance == 1:
                    axs = [axs]
            elif plot_type == 'each':
                if n_instance > 1:
                    axs = np.ndarray((row, col))
                else:
                    axs = np.array(1)

            instances_iter = instances  # add sorted
            for instance, ax in zip(instances_iter, iter_axs(axs, col)):
                if plot_type == 'each':
                    fig, ax = plt.subplots()
                solver_names = set(s for d, i, s in self.logs if (d, i) == (dataset, instance))
                for solver_name in solver_names:
                    log = self.logs[dataset, instance, solver_name]
                    log.plot(
                        show=False, xitem=xitem, linestyle='--', marker='.',
                        label=solver_name, fig=fig, ax=ax
                    )
                setax(ax, instance, yscale)
                if plot_type == 'each':
                    if save_prefix is None:
                        plt.show()
                    else:
                        save_fig(fig, f'{save_prefix}{dataset}/{instance}.pdf')

        if plot_type == 'all':
            if save_prefix is None:
                plt.show()
            else:
                save_fig(fig, f'{save_prefix}{dataset}.pdf')


    def stat(self, time=None, iteration=None):
        """display static information

        Parameters
        ----------
        time : int or float
            summary logs whose time less than time
        iteration : int
            summary logs whose iteration less than iteration
        """
        logger.debug(f'summary logs time={time}, iteration={iteration}')
        datasets = set(dataset for dataset, _, _ in self.logs)
        for dataset in datasets:
            stat_message_header = [
                "","",
                f"{dataset}",
                "="*len(dataset),
                ""
            ]
            solvers = sorted(set(s for d, _, s in self.logs if d == dataset))
            instances = sorted(set(i for d, i, _ in self.logs if d == dataset))
            stat_messages = []
            stat = {
                'num_wins': [0]*len(solvers),
                'score': [0]*len(solvers)
            }
            for instance in instances:
                stat_message = [instance]
                obj_values = []
                for i, solver in enumerate(solvers):
                    if (dataset, instance, solver) in self.logs:
                        logs = self.logs[dataset, instance, solver]
                        log = logs.getLog(time=time, iteration=iteration)
                        obj_value = log['obj_value']
                        stat_message.append(value2str(obj_value))
                        obj_values.append(obj_value)
                    else:
                        stat_message.append('')
                        obj_values.append(float('inf'))
                stat_messages.append(stat_message)
                sorted_solver_ixs = np.argsort(obj_values)
                win_solver_ix = sorted_solver_ixs[0]
                stat['num_wins'][win_solver_ix] += 1

                best_obj = obj_values[sorted_solver_ixs[0]]
                n_win = 1
                while n_win < len(obj_values):
                    obj = obj_values[sorted_solver_ixs[n_win]]
                    if abs(best_obj - obj) < 1e-10:
                        stat['num_wins'][sorted_solver_ixs[n_win]] += 1
                        n_win += 1
                    else:
                        break
                for i, solver_ix in enumerate(sorted_solver_ixs):
                    if i < n_win:
                        stat['score'][solver_ix] += 0
                    else:
                        stat['score'][solver_ix] += i


            print("\n".join(stat_message_header))
            messages = []
            messages.append(["Instance"] + solvers)
            messages.append(["-"*8] + ["-"*len(s) for s in solvers])
            messages += stat_messages
            messages.append([''])
            messages.append(['#Win'] + list(map(str, stat['num_wins'])))
            messages.append(['Score'] + list(map(str, stat['score'])))
            # simple ranking
            sorted_solver_ix = np.argsort(stat['score'])
            ranks = [0]*len(solvers)
            for i, solver_ix in enumerate(sorted_solver_ix, 1):
                ranks[solver_ix] = i
            messages.append(['Ranking'] + list(map(str, ranks)))

            arr_dict = defaultdict(int)
            for message in messages:
                for col, el in enumerate(message):
                    arr_dict[col] = max(arr_dict[col], len(el))
            for i, message in enumerate(messages):
                message = [
                    '{}{}'.format(' '*(arr_dict[col]-len(el)), el)
                    for col, el in enumerate(message)
                ]
                messages[i] = message
            for message in messages:
                print(' '.join(message))


    def __len__(self):
        return len(self.logs)


def save_fig(fig, path):
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    fig.savefig(path, bbox_inches='tight')
    plt.close()


def iter_axs(axs, col):
    i = 0; j = 0
    while True:
        if col > 1:
            yield axs[i, j]
        else:
            yield axs[j]
        if j < col-1:
            j += 1
        else:
            i, j = i+1, 0


def setax(ax, title, yscale):
    ax.grid('--')
    ax.legend()
    ax.set_title(title)
    ax.set_yscale(yscale)

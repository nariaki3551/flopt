import os
import pickle
from math import ceil
from glob import glob
from itertools import product
from collections import defaultdict
import matplotlib.pyplot as plt

from flopt import env as flopt_env

performance_dir = flopt_env.performance_dir


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

    def plot(self, xitem='time', col=2):
        """
        plot logs

        Parameters
        ----------
        xitem : str
          x-label name. 'time' or 'iteration'
        col : int
          #columns of figure
        """
        datasets = set(dataset for dataset, _, _ in self.logs)
        for dataset in datasets:
            instances = set(i for d, i, _ in self.logs if d == dataset)
            n_instance = len(instances)
            col = 1 if n_instance < 2 else col
            row = ceil(n_instance/col)
            fig, axs = plt.subplots(row, col)
            if n_instance == 1:
                axs = [axs]

            fig.suptitle(dataset)
            instances_iter = instances  # add sorted
            for instance, ax in zip(instances_iter, iter_axs(axs, col)):
                solver_names = set(s for d, i, s in self.logs if (d, i) == (dataset, instance))
                for solver_name in solver_names:
                    log = self.logs[dataset, instance, solver_name]
                    log.plot(
                        show=False, xitem=xitem, linestyle='--', marker='.',
                        label=solver_name, fig=fig, ax=ax
                    )
                setax(ax, instance)
            plt.show()

    def __len__(self):
        return len(self.logs)


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


def setax(ax, title):
    ax.grid('--')
    ax.legend()
    ax.set_title(title)

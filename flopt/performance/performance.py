import os
import pickle
from itertools import product

from flopt import env as flopt_env
from flopt import Problem, Solver, Solver_list
from .custom_dataset import CustomDataset
from .log_visualizer import LogVisualizer

performance_dir = flopt_env.performance_dir


def compute(datasets, solvers='all', 
    timelimit=None, msg=True, save_prefix=None):
    """
    Measure the performance of (dataset, solver)

    Parameters
    ----------
    datasets : list of Dataset or Dataset or Problem
        datasets
    solvers  : list of solvers or solver
        solvers
    timelimit : float
        timelimit
    msg : bool
        if true, then display log during solve
    save_prefix : str
        the path in which each log is saved

    Returns
    -------
    dict
        logs; logs[solver.name, dataset.name, instance.name] = log

    Examples
    --------

    We calculate the performance of (dataset, solver).

    .. code-block:: python

        from flopt import Solver
        import flopt

        # datasets
        tsp_dataset = flopt.performance.datasets['tsp']
        func_dataset = flopt.performance.datasets['func']

        # compute the performance
        logs = flopt.performance.compute([func_dataset, tsp_dataset], timelimit=2, msg=True)

        # visualize the performance
        log_visualizer = flopt.performance.LogVisualizer(logs)
        lov_visualizer.plot()


    We can select the solver to calculate the performance.

    .. code-block:: python

        rs_solver = Solver('RandomSearch')

        # compute the performance
        logs = flopt.performance.compute(
            [func_dataset, tsp_dataset],  # dataset list
            [rs_solver],  # solver list
            timelimit=2,
            msg=True
        )

        # visualize the performance
        log_visualizer = flopt.performance.LogVisualizer(logs)
        lov_visualizer.plot()
        
    
    We can use user defined problem as dataset

    .. code-block:: python

      # prob is user defined problem
      flopt.performance.compute(prob, timelimit=2, msg=True)

    """
    # datasets settings
    if isinstance(datasets, Problem):
      cd = CustomDataset(name='user', probs=[datasets])
      datasets = [cd]
    elif not isinstance(datasets, list):
        datasets = [datasets]

    # solvers settings
    if solvers == 'all':
        solvers = [Solver(algo=algo) for algo in Solver_list()]
    elif not isinstance(solvers, list):
        solvers = [solvers]
    for solver in solvers:
        if timelimit is not None:
            solver.setParams(timelimit=timelimit)

    # save_prefix setting
    if save_prefix is None:
        save_prefix = performance_dir

    logs = dict()

    for dataset in datasets:
        for instance in dataset:
            for solver in solvers:
                solver.reset()
                formulatable, prob = instance.createProblem(solver)
                if not formulatable:
                    continue
                state, log = prob.solve(solver=solver, msg=msg)
                save_log(log, solver, dataset, instance, save_prefix)
                logs[dataset.name, instance.name, solver.name] = log
    return logs


def save_log(log, solver, dataset, instance, save_prefix):
    """
    save log as save_prefix/solver.name/dataset.name/instance.name/log.pickle
    """
    save_dir = f'{save_prefix}/{solver.name}/{dataset.name}/{instance.name}'
    os.makedirs(save_dir, exist_ok=True)
    with open(f'{save_dir}/log.pickle', 'wb') as pf:
        pickle.dump(log, pf)


def performance(datasets, solver_names=Solver_list(),
    xitem='time', load_prefix=None):
    """
    plot performance of each (dataset, algo) where algo is solver.name

    Parameters
    ----------
    datasets : list of Dataset or a Problem
      datasets name
    solver_names : list of str
      solver names
    xitem : str
      x-label item of figure (time or iteration)
    load_prefix : str
      the path in which each log is saved

    See Also
    --------
    flopt.performance.compute
    """
    if isinstance(datasets, list):
        dataset_names = [dataset.name for dataset in datasets]
    elif isinstance(datasets, Problem):
        dataset_names = ['user']
    else:
        dataset_names = [datasets.name]
    if not isinstance(solver_names, list):
        solver_names = [solver_names]
    if load_prefix is None:
        load_prefix = performance_dir

    log_visualizer = LogVisualizer()
    log_visualizer.load(
        solver_names=solver_names,
        datasets=dataset_names,
    )
    log_visualizer.plot(xitem=xitem)

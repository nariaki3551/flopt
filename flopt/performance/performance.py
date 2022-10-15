import os
import pickle
from itertools import product

from flopt import Problem, Solver, Solver_list
import flopt.solvers
import flopt.env
from flopt.env import setup_logger

from .custom_dataset import CustomDataset
from .log_visualizer import LogVisualizer

PERFORMANCE_DIR = flopt.env.PERFORMANCE_DIR
logger = setup_logger(__name__)


def compute(
    datasets, solvers="all", timelimit=None, msg=True, save_prefix=None, **kwargs
):
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

        import flopt

        # datasets
        tsp_dataset = flopt.performance.get_dataset("tsp")
        func_dataset = flopt.performance.get_dataset("func")

        # compute the performance
        logs = flopt.performance.compute([func_dataset, tsp_dataset], timelimit=2, msg=True)

        # visualize the performance
        log_visualizer = flopt.performance.LogVisualizer(logs)
        log_visualizer.plot()


    We can select the solver to calculate the performance.

    .. code-block:: python

        rs_solver = flopt.Solver("RandomSearch")

        # compute the performance
        logs = flopt.performance.compute(
            [func_dataset, tsp_dataset],  # dataset list
            [rs_solver],  # solver list
            timelimit=2,
            msg=True
        )

        # visualize the performance
        log_visualizer = flopt.performance.LogVisualizer(logs)
        log_visualizer.plot()


    We can use user defined problem as dataset

    .. code-block:: python

      # prob is user defined problem
      flopt.performance.compute(prob, timelimit=2, msg=True)

    """
    assert timelimit is not None, "timelimit is required"
    # datasets settings
    if isinstance(datasets, Problem):
        cd = CustomDataset(name="user", probs=[datasets])
        datasets = [cd]
    elif not isinstance(datasets, list):
        datasets = [datasets]

    # solvers settings
    if solvers == "all":
        solvers = [Solver(algo=algo) for algo in Solver_list()]
    elif not isinstance(solvers, list):
        solvers = [solvers]
    for solver in solvers:
        solver.setParams(timelimit=timelimit, **kwargs)

    # save_prefix setting
    if save_prefix is None:
        save_prefix = PERFORMANCE_DIR

    logs = dict()

    for dataset in datasets:
        for instance in dataset:
            logger.info(instance)
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
    save_dir = f"{save_prefix}/{solver.name}/{dataset.name}/{instance.name}"
    os.makedirs(save_dir, exist_ok=True)
    with open(f"{save_dir}/log.pickle", "wb") as pf:
        pickle.dump(log, pf)


def performance(
    datasets,
    solver_names=None,
    xitem="time",
    yscale="linear",
    plot_type="all",
    save_prefix=None,
    time=None,
    iteration=None,
    load_prefix=None,
):
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
    yscale : str
        linear or log
    plot_type : str
        all: create figures for each dataset.
        each: create figures for each instance.
        noshow: do not create figures.
    save_prefix : str
        prefix of fig save name
    time : int or float
        summary logs whose time less than time
    iteration : int
        summary logs whose iteration less than iteration
    load_prefix : str
        the path in which each log is saved

    See Also
    --------
    flopt.performance.compute
    """
    if isinstance(datasets, list):
        dataset_names = [dataset.name for dataset in datasets]
    elif isinstance(datasets, Problem):
        dataset_names = ["user"]
    else:
        dataset_names = [datasets.name]
    if solver_names is None:
        solver_names = Solver_list()
    elif not isinstance(solver_names, list):
        solver_names = [solver_names]
    if load_prefix is None:
        load_prefix = PERFORMANCE_DIR

    log_visualizer = LogVisualizer()
    log_visualizer.load(
        solver_names=solver_names,
        datasets=dataset_names,
        load_prefix=load_prefix,
    )

    if not plot_type == "noshow":
        log_visualizer.plot(
            xitem=xitem, yscale=yscale, plot_type=plot_type, save_prefix=save_prefix
        )

    log_visualizer.stat(time=time, iteration=iteration)

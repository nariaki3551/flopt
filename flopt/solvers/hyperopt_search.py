import weakref

import hyperopt

from flopt.solvers.base import BaseSearch
from flopt.constants import VariableType, ExpressionType, SolverTerminateState
from flopt.env import setup_logger


import logging

loggers_to_shut_up = [
    "hyperopt.tpe",
    "hyperopt.fmin",
    "hyperopt.pyll.base",
]
for logger in loggers_to_shut_up:
    logging.getLogger(logger).setLevel(logging.ERROR)


logger = setup_logger(__name__)


class HyperoptTPESearch(BaseSearch):
    """
    TPE Search using Hyperopt (https://hyperopt.github.io/hyperopt/)

    Parameters
    ----------
    n_trial : int
        number of trials
    show_progressbar : bool
        whether display a progress bar of search

    Examples
    --------

    .. code-block:: python

        import flopt

        x = flopt.Variable("x", lowBound=-1, upBound=1, cat="Continuous")
        y = flopt.Variable("y", lowBound=-1, upBound=1, cat="Continuous")

        prob = flopt.Problem()
        prob += 2*x*x + x*y + y*y + x + y

        solver = flopt.Solver("HyperoptTPESearch")
        status, log = prob.solve(solver, msg=True, timelimit=1)

        print("obj =", flopt.Value(prob.obj))
        print("x =", flopt.Value(x))
        print("y =", flopt.Value(y))
    """

    name = "HyperoptTPESearch"
    can_solve_problems = {
        "Variable": VariableType.Number,
        "Objective": ExpressionType.Any,
        "Constraint": ExpressionType.Non,
    }

    def __init__(self):
        super().__init__()
        from hyperopt import STATUS_OK

        self.n_trial = 1e100
        self.show_progressbar = False
        self.hyperopt_STATUS_OK = STATUS_OK

    def search(self, solution, *args):

        self.start_build()

        # make the search space
        space = dict()
        for var in solution:
            name = var.name
            lb = var.getLb(must_number=True)
            ub = var.getUb(must_number=True)
            if var.type() in {
                VariableType.Integer,
                VariableType.Binary,
                VariableType.Spin,
            }:
                var_space = hyperopt.hp.quniform(name, lb, ub, 1)
            elif var.type() == VariableType.Continuous:
                var_space = hyperopt.hp.uniform(name, lb, ub)
            space[var.name] = var_space

        def objective_func(var_value_dict):
            # set value into solution
            for name, value in var_value_dict.items():
                if var.type() == VariableType.Spin:
                    value = 2 * value - 1  # binary -> spin
                solution.setValue(name, value)
            obj_value = self.getObjValue(solution)

            # update best solution if needed
            self.registerSolution(solution, obj_value)

            # execute callbacks
            self.callback([solution])

            # check timelimit
            self.raiseTimeoutIfNeeded()

            return {"loss": obj_value, "status": self.hyperopt_STATUS_OK}

        self.end_build()

        # search
        hyperopt.fmin(
            objective_func,
            space=space,
            algo=hyperopt.tpe.suggest,
            max_evals=self.n_trial,
            show_progressbar=self.show_progressbar,
        )

        return SolverTerminateState.Normal

import weakref

import hyperopt

from flopt.env import setup_logger
from flopt.solvers.base import BaseSearch
from flopt.solvers.solver_utils import (
    during_solver_message,
)
from flopt.constants import VariableType, SolverTerminateState


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
    """

    name = "HyperoptTPESearch"
    can_solve_problems = ["blackbox"]

    def __init__(self):
        super().__init__()
        from hyperopt import STATUS_OK

        self.n_trial = 1e100
        self.show_progressbar = False
        self.hyperopt_STATUS_OK = STATUS_OK

    def available(self, prob, verbose=False):
        """
        Parameters
        ----------
        prob : Problem
        verbose : bool

        Returns
        -------
        bool
            return true if it can solve the problem else false
        """
        for var in prob.getVariables():
            if not var.type() in {
                VariableType.Continuous,
                VariableType.Integer,
                VariableType.Binary,
            }:
                if verbose:
                    logger.error(
                        f"variable: \n{var}\n must be continuous, integer, or binary, but got {var.type()}"
                    )
                return False
        if prob.constraints:
            if verbose:
                logger.error(f"this solver can not handle constraints")
            return False
        return True

    def search(self):

        self.start_build()

        # make the search space
        space = dict()
        for var in self.solution:
            name = var.name
            lb = var.getLb(must_number=True)
            ub = var.getUb(must_number=True)
            if var.type() in {name, VariableType.Integer, VariableType.Binary}:
                var_space = hyperopt.hp.quniform(name, lb, ub, 1)
            elif var.type() == VariableType.Continuous:
                var_space = hyperopt.hp.uniform(name, lb, ub)
            space[var.name] = var_space

        # for objective
        self.var_dict = weakref.WeakValueDictionary(
            {var.name: var for var in self.solution}
        )

        self.end_build()

        # search
        hyperopt.fmin(
            self.objective,
            space=space,
            algo=hyperopt.tpe.suggest,
            max_evals=self.n_trial,
            show_progressbar=self.show_progressbar,
        )

        return SolverTerminateState.Normal

    def objective(self, var_value_dict):
        # set value into self.solution
        self.trial_ix += 1
        for name, value in var_value_dict.items():
            self.var_dict[name].setValue(value)
        obj_value = self.getObjValue(self.solution)

        # if solution is better thatn incumbent, then update best solution
        self.registerSolution(self.solution, obj_value)

        # callbacks
        for callback in self.callbacks:
            callback([self.solution], self.best_solution, self.best_obj_value)

        # check timelimit
        self.raiseTimeoutIfNeeded()

        return {"loss": obj_value, "status": self.hyperopt_STATUS_OK}

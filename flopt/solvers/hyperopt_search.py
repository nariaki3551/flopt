from time import time

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
    def __init__(self):
        super().__init__()
        from hyperopt import STATUS_OK
        self.name = 'HyperoptTPESearch'
        self.n_trial = 1e100
        self.show_progressbar = False
        self.can_solve_problems = ['blackbox']
        self.hyperopt_STATUS_OK = STATUS_OK


    def available(self, prob):
        """
        Parameters
        ----------
        obj : Expression or VarElement family
            objective function
        constraints : list of Constraint
            constraints

        Returns
        -------
        bool
            return true if it can solve the problem else false
        """
        return all(
                var.type() in {VariableType.Continuous, VariableType.Integer, VariableType.Binary}
                for var in prob.getVariables()
                ) and ( not prob.constraints )


    def search(self):
        import hyperopt
        status = SolverTerminateState.Normal

        # make the search space
        space = dict()
        for var in self.solution:
            name = var.name
            if var.type() in {name, VariableType.Integer, VariableType.Binary}:
                var_space = hyperopt.hp.quniform(name, var.getLb(), var.getUb(), 1)
            elif var.type() == VariableType.Continuous:
                var_space = hyperopt.hp.uniform(name, var.getLb(), var.getUb())
            space[var.name] = var_space

        # for objective
        self.var_dict = {var.name: var for var in self.solution}

        # search
        try:
            hyperopt.fmin(
                self.objective, space=space,
                algo=hyperopt.tpe.suggest,
                max_evals=self.n_trial,
                show_progressbar=self.show_progressbar,
            )
        except TimeoutError:
            status = SolverTerminateState.Timelimit

        return status


    def objective(self, var_value_dict):
        # check timelimit
        if time() > self.start_time + self.timelimit:
            raise TimeoutError

        # set value into self.solution
        self.trial_ix += 1
        for name, value in var_value_dict.items():
            self.var_dict[name].setValue(value)
        obj_value = self.getObjValue(self.solution)

        # check whether update or not
        if obj_value < self.best_obj_value:
            self.updateSolution(self.solution, obj_value)
            self.recordLog()
            if self.msg:
                self.during_solver_message('*')

        # callbacks
        for callback in self.callbacks:
            callback([self.solution], self.best_solution, self.best_obj_value)

        return {'loss': obj_value, 'status': self.hyperopt_STATUS_OK}



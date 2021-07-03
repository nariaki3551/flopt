from time import time

from flopt.solvers.base import BaseSearch
from flopt.solvers.solver_utils import (
    Log, start_solver_message,
    during_solver_message_header,
    during_solver_message,
    end_solver_message
)
from flopt.env import setup_logger
import flopt.constants


logger = setup_logger(__name__)


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
        return all(not var.getType() == 'VarPermutation' for var in prob.getVariables())\
                and (not prob.constraints)


    def search(self):
        import hyperopt
        if self.constraints:
            logger.error("This Solver does not support the problem with constraints.")
            status = flopt.constants.SOLVER_ABNORMAL_TERMINATE
            return status

        self.startProcess()
        status = flopt.constants.SOLVER_NORMAL_TERMINATE

        # make the search space
        space = self.gen_space()
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
            status = flopt.constants.SOLVER_TIMELIMIT_TERMINATE

        self.closeProcess()
        return status


    def gen_space(self):
        """
        generate search space
        """
        from hyperopt import hp
        space = dict()
        for var in self.solution:
            name = var.name
            if var.getType() in {name, 'VarInteger' , 'VarBinary'}:
                var_space = hp.quniform(name, var.lowBound, var.upBound, 1)
            elif var.getType() == 'VarContinuous':
                var_space = hp.uniform(name, var.lowBound, var.upBound)
            space[var.name] = var_space
        return space


    def objective(self, var_value_dict):
        # check timelimit
        if time() > self.start_time + self.timelimit:
            raise TimeoutError

        # set value into self.solution
        self.trial_ix += 1
        for name, value in var_value_dict.items():
            self.var_dict[name].setValue(value)
        obj_value = self.obj.value(self.solution)

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


    def startProcess(self):
        self.best_obj_value = self.obj.value(self.best_solution)
        self.recordLog()

        if self.msg:
            during_solver_message_header()
            self.during_solver_message('S')


    def closeProcess(self):
        self.recordLog()

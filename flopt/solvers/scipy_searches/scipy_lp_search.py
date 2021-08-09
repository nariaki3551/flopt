from time import time

from scipy import optimize as scipy_optimize
import numpy as np

from flopt.solvers.base import BaseSearch
from flopt.solvers.solver_utils import (
    Log, start_solver_message,
    during_solver_message_header,
    during_solver_message,
    end_solver_message
)
from flopt.convert import flopt_to_lp
from flopt.env import setup_logger
from flopt.variable import VarConst
from flopt.solution import Solution
import flopt.constants


logger = setup_logger(__name__)


class ScipyLpSearch(BaseSearch):
    def __init__(self):
        super().__init__()
        self.name = "ScipyLpSearch"
        self.n_trial = 1e10
        self.method = 'simplex'


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
        print([var.getType() == 'VarContinuous' for var in prob.getVariables()])
        return all(var.getType() == 'VarContinuous' for var in prob.getVariables())


    def search(self):
        self.startProcess()
        status = self._search()
        self.closeProcess()
        return status


    def _search(self):
        status = flopt.constants.SOLVER_NORMAL_TERMINATE
        lp = flopt_to_lp(self.prob)

        # bounds
        bounds = [ (_lb, _ub) for _lb, _ub in zip(lp.lb, lp.ub) ]

        # options
        options = {'maxiter': self.n_trial, 'disp': self.msg}

        # callback
        def callback(values, **kwargs):
            self.trial_ix += 1
            obj_value = func(values)
            for var, value in zip(self.solution, values):
                var.setValue(value)
            if time() > self.start_time + self.timelimit:
                raise TimeoutError
            if obj_value < self.best_obj_value:
                diff = self.best_obj_value - obj_value
                self.updateSolution(self.solution, obj_value)
                self.recordLog()
                if self.msg and diff > 1e-8:
                    self.during_solver_message('*')
            for _callback in self.callbacks:
                _callback([self.solution], self.best_solution, self.best_obj_value)

        try:
            res = scipy_optimize.linprog(
                c=lp.c, A_ub=lp.A, b_ub=lp.b, bounds=bounds,
                options=options,
                callback=callback, method=self.method,
                )
            # get result of solver
            for var, value in zip(self.solution, res.x):
                var.setValue(value)
            self.updateSolution(self.solution, obj_value=None)
        except TimeoutError:
            status = flopt.constants.SOLVER_TIMELIMIT_TERMINATE

        return status


    def startProcess(self):
        self.best_obj_value = self.obj.value(self.best_solution)
        self.recordLog()

        if self.msg:
            during_solver_message_header()
            self.during_solver_message('S')


    def closeProcess(self):
        self.recordLog()

from time import time

import scipy
import numpy as np

from flopt.solvers.base import BaseSearch
from flopt.solvers.solver_utils import (
    Log, start_solver_message,
    during_solver_message_header,
    during_solver_message,
    end_solver_message
)
from flopt.env import setup_logger
from flopt.variable import VarConst
from flopt.solution import Solution
import flopt.constants


logger = setup_logger(__name__)


class ScipySearch(BaseSearch):
    def __init__(self):
        super().__init__()
        self.name = "ScipySearch"
        self.n_trial = 1e10
        self.method = None
        self.can_solve_problems = ['blackbox']


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
        return all(not var.getType() == 'VarPermutation' for var in prob.getVariables())


    def search(self):
        self.startProcess()
        status = self._search()
        self.closeProcess()
        return status


    def _search(self):
        status = flopt.constants.SOLVER_NORMAL_TERMINATE
        var_names = [var.name for var in self.solution]

        def gen_func(expression):
            def func(values):
                variables = []
                for var_name, value in zip(var_names, values):
                    variables.append(VarConst(var_name, value))
                solution = Solution('tmp', variables)
                return expression.value(solution)
            return func

        # function
        func = gen_func(self.obj)

        # initial point
        self.solution.setRandom()
        x0 = [var.value() for var in self.solution]

        # bounds
        lb = [var.lowBound for var in self.solution]
        ub = [var.upBound for var in self.solution]
        bounds = scipy.optimize.Bounds(lb, ub, keep_feasible=False)

        # constraints
        constraints = []
        for const in self.constraints:
            const_func = gen_func(const)
            lb, ub = 0, 0
            if const.type == 'le':
                lb = -np.inf
            elif const.type == 'ge':
                ub = np.inf
            nonlinear_const = \
                scipy.optimize.NonlinearConstraint(const_func, lb, ub)
            constraints.append(nonlinear_const)

        # options
        options = {'maxiter': self.n_trial}

        # callback
        def callback(values):
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
            res = scipy.optimize.minimize(
                func, x0, bounds=bounds, constraints=constraints, options=options,
                callback=callback, args=(), method=self.method,
                jac=None, hess=None, hessp=None, tol=None,
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

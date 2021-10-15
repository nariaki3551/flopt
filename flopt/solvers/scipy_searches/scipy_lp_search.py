from time import time

from scipy import optimize as scipy_optimize
import numpy as np

from flopt.solvers.base import BaseSearch
from flopt.solvers.solver_utils import (
    during_solver_message,
    end_solver_message
)
from flopt.convert import LpStructure
from flopt.env import setup_logger
from flopt.expression import Const
from flopt.solution import Solution
from flopt.constants import VariableType, SolverTerminateState


logger = setup_logger(__name__)


class ScipyLpSearch(BaseSearch):
    """Scipy optimize linprog API Solver

    See Also
    --------
    scipy.optimize.linprog

    Returns
    -------
    status : int
        status of solver
    """
    def __init__(self):
        super().__init__()
        self.name = "ScipyLpSearch"
        self.n_trial = 1e10
        self.method = 'simplex'
        self.can_solve_problems = ['lp']


    def available(self, prob):
        """
        Parameters
        ----------
        prob : Problem

        Returns
        -------
        bool
            return true if it can solve the problem else false
        """
        if prob.obj.isLinear()\
            and all(const.expression.isLinear() for const in prob.constraints)\
            and all(var.type() == VariableType.Continuous for var in prob.getVariables()):
            return True
        else:
            return False


    def search(self):
        status = SolverTerminateState.Normal
        var_names = [var.name for var in self.solution]

        def gen_func(expression):
            def func(values):
                variables = []
                for var_name, value in zip(var_names, values):
                    variables.append(Const(value, name=var_name))
                solution = Solution('tmp', variables)
                return expression.value(solution)
            return func

        # function
        func = gen_func(self.prob.obj)

        # lp structure
        lp = LpStructure.fromFlopt(self.prob, x=self.solution.getVariables())

        # bounds
        bounds = [ (_lb, _ub) for _lb, _ub in zip(lp.lb, lp.ub) ]

        # options
        options = {'maxiter': self.n_trial, 'disp': self.msg}

        # callback
        def callback(optimize_result):
            self.trial_ix += 1
            obj_value = func(optimize_result.x)
            for var, value in zip(self.solution, optimize_result.x):
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

        # search
        try:
            res = scipy_optimize.linprog(
                c=lp.c,
                A_ub=lp.A, b_ub=lp.b,
                A_eq=lp.G, b_eq=lp.h,
                bounds=bounds,
                options=options,
                callback=callback, method=self.method,
                )
            # get result of solver
            for var, value in zip(self.solution, res.x):
                var.setValue(value)
            self.updateSolution(self.solution, obj_value=None)
        except TimeoutError:
            status = SolverTerminateState.Timelimit

        return status


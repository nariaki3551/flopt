from time import time

from scipy import optimize as scipy_optimize
import numpy as np

from flopt.solvers.base import BaseSearch
from flopt.solvers.solver_utils import (
    during_solver_message,
)
from flopt.env import setup_logger
from flopt.expression import Const
from flopt.solution import Solution
from flopt.constants import VariableType, SolverTerminateState


logger = setup_logger(__name__)


class ScipySearch(BaseSearch):
    """scipy optimize minimize API Solver

    See Also
    --------
    scipy.optimize.minimize
    """
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
        prob : Problem

        Returns
        -------
        bool
            return true if it can solve the problem else false
        """
        return all(var.type() == VariableType.Continuous for var in prob.getVariables())


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

        # initial point
        self.solution.setRandom()
        x0 = [var.value() for var in self.solution]

        # bounds
        lb = [var.getLb() for var in self.solution]
        ub = [var.getUb() for var in self.solution]
        bounds = scipy_optimize.Bounds(lb, ub, keep_feasible=False)

        # constraints
        constraints = []
        for const in self.prob.constraints:
            const_func = gen_func(const)
            lb, ub = 0, 0
            if const.type == 'le':
                lb = -np.inf
            elif const.type == 'ge':
                ub = np.inf
            nonlinear_const = \
                scipy_optimize.NonlinearConstraint(const_func, lb, ub)
            constraints.append(nonlinear_const)

        # options
        options = {'maxiter': self.n_trial}

        # callback
        def callback(values, ):
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
            res = scipy_optimize.minimize(
                func, x0, bounds=bounds, constraints=constraints, options=options,
                callback=callback, args=(), method=self.method,
                jac=None, hess=None, hessp=None, tol=None,
            )
            # get result of solver
            for var, value in zip(self.solution, res.x):
                var.setValue(value)
            self.updateSolution(self.solution, obj_value=None)
        except TimeoutError:
            status = SolverTerminateState.Timelimit

        return status


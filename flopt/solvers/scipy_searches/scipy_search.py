import time

from scipy import optimize as scipy_optimize
import numpy as np

from flopt.solvers.base import BaseSearch
from flopt.env import setup_logger
from flopt.expression import Const
from flopt.solution import Solution
from flopt.constants import VariableType, ConstraintType, SolverTerminateState


logger = setup_logger(__name__)


class ScipySearch(BaseSearch):
    """scipy optimize minimize API Solver

    See Also
    --------
    scipy.optimize.minimize
    """

    name = "ScipySearch"
    can_solve_problems = ["blackbox"]

    def __init__(self):
        super().__init__()
        self.n_trial = 1e10
        self.method = None

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
            if not var.type() == VariableType.Continuous:
                if verbose:
                    logger.error(
                        f"variable: \n{var}\n must be continouse, but got {var.type()}"
                    )
                return False
        return True

    def search(self):
        var_names = [var.name for var in self.solution]

        def gen_func(expression):
            def func(values):
                variables = []
                for var_name, value in zip(var_names, values):
                    variables.append(Const(value, name=var_name))
                solution = Solution("tmp", variables)
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
            if const.type == ConstraintType.Le:
                lb = -np.inf
            nonlinear_const = scipy_optimize.NonlinearConstraint(const_func, lb, ub)
            constraints.append(nonlinear_const)

        # options
        options = {"maxiter": self.n_trial}

        # callback
        def callback(
            values,
        ):
            self.trial_ix += 1
            for var, value in zip(self.solution, values):
                var.setValue(value)
            if time.time() > self.start_time + self.timelimit:
                raise TimeoutError

            # if solution is better thatn incumbent, then update best solution
            self.registerSolution(self.solution, msg_tol=1e-8)

            # callbacks
            for _callback in self.callbacks:
                _callback([self.solution], self.best_solution, self.best_obj_value)

        try:
            res = scipy_optimize.minimize(
                func,
                x0,
                bounds=bounds,
                constraints=constraints,
                options=options,
                callback=callback,
                args=(),
                method=self.method,
                jac=None,
                hess=None,
                hessp=None,
                tol=None,
            )
            # get result of solver
            for var, value in zip(self.solution, res.x):
                var.setValue(value)
            self.updateSolution(self.solution, obj_value=None)
        except TimeoutError:
            return SolverTerminateState.Timelimit

        return SolverTerminateState.Normal

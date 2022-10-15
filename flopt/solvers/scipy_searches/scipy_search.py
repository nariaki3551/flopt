from scipy import optimize as scipy_optimize
import numpy as np

from flopt.solvers.base import BaseSearch
from flopt.expression import Const
from flopt.solution import Solution
from flopt.constants import (
    VariableType,
    ExpressionType,
    ConstraintType,
    SolverTerminateState,
)
from flopt.env import setup_logger


logger = setup_logger(__name__)


class ScipySearch(BaseSearch):
    """scipy optimize minimize API Solver

    Examples
    --------

    .. code-block:: python

        import flopt

        # Variables
        a = flopt.Variable("a", lowBound=-2, upBound=1, cat="Integer")
        b = flopt.Variable("b", lowBound=1, upBound=4, cat="Continuous")
        c = flopt.Variable("c", lowBound=0, upBound=3, cat="Continuous")

        # Problem
        prob = flopt.Problem()
        prob += a*a + a*b + b + c + 2
        prob += a + b >= 2
        prob += b - c == 3

        solver = flopt.Solver("ScipySearch")
        prob.solve(solver, msg=True)

        print(flopt.Value([a, b, c]))
        >>> [0, 2.9999999999999996, 0.0]


    See Also
    --------
    scipy.optimize.minimize
    """

    name = "ScipySearch"
    can_solve_problems = {
        "Variable": VariableType.Number,
        "Objective": ExpressionType.Any,
        "Constraint": ExpressionType.Any,
    }

    def __init__(self):
        super().__init__()
        self.n_trial = 1e8
        self.method = None

    def search(self, solution, objective, constraints):
        self.start_build()

        def gen_func(expression):
            def func(values):
                # check timelimit
                self.raiseTimeoutIfNeeded()

                for var, value in zip(solution, values):
                    if var.type() == VariableType.Spin:
                        value = 2 * value - 1
                    if not var.type() == VariableType.Continuous:
                        value = round(value)
                    var.setValue(value)
                try:
                    return expression.value(solution)
                except OverflowError:
                    return float("inf")

            return func

        # initial point
        x0 = [var.value() for var in solution]

        # bounds
        lb, ub = list(), list()
        for var in solution:
            if var.type() == VariableType.Spin:
                lb.append(0)
                ub.append(1)
            else:
                lb.append(l if (l := var.getLb()) is not None else -np.inf)
                ub.append(u if (u := var.getUb()) is not None else np.inf)
        bounds = scipy_optimize.Bounds(lb, ub, keep_feasible=False)

        # constraints
        scipy_constraints = []
        for const in constraints:
            const_func = gen_func(const)
            lb, ub = 0, 0
            if const.type() == ConstraintType.Le:
                lb = -np.inf
            nonlinear_const = scipy_optimize.NonlinearConstraint(const_func, lb, ub)
            scipy_constraints.append(nonlinear_const)

        # options
        options = {"maxiter": self.n_trial}

        # callback for scipy
        def callback(values):
            for var, value in zip(solution, values):
                if var.type() == VariableType.Spin:
                    value = 2 * value - 1  # binary -> spin
                if not var.type() == VariableType.Continuous:
                    value = round(value)
                var.setValue(value)

            # update best solution if needed
            self.registerSolution(solution, msg_tol=1e-8)

            # callbacks
            self.callback([solution])

        self.end_build()

        res = scipy_optimize.minimize(
            gen_func(objective),
            x0,
            bounds=bounds,
            constraints=scipy_constraints,
            options=options,
            callback=callback,
            args=(),
            method=self.method,
            jac=None,
            hess=None,
            hessp=None,
            tol=None,
        )

        if res.success:
            # get result of solver
            solution.setValuesFromArray(res.x)
            self.registerSolution(solution)
            return SolverTerminateState.Normal
        else:
            logger.warning(f"ScipySearch cound not success to find solution.")
            return SolverTerminateState.Abnormal

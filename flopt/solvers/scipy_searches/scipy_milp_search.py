from scipy import optimize as scipy_optimize
import numpy as np

from flopt.solvers.base import BaseSearch
from flopt.convert import LpStructure
from flopt.variable import VariableArray
from flopt.constants import VariableType, ExpressionType, SolverTerminateState
from flopt.env import setup_logger


logger = setup_logger(__name__)


class ScipyMilpSearch(BaseSearch):
    """Scipy optimize milp API Solver

    Note
    ----
    In scipy version 1.9.0,
    we can not obtain the incumbent solution from scipy.optimize.milp API,
    and can not use callback to this API for logging.
    Therefore, we can obtain the solution when only scipy.optimize.milp terminate the execution normally.

    Examples
    --------

    .. code-block:: python

        import flopt

        # Variables
        a = flopt.Variable("a", lowBound=0, upBound=1, cat="Integer")
        b = flopt.Variable("b", lowBound=1, upBound=2, cat="Continuous")
        c = flopt.Variable("c", lowBound=-1, upBound=3, cat="Continuous")

        # Problem
        prob = flopt.Problem()
        prob += a + b + c + 2
        prob += a + b >= 2
        prob += b - c >= 3

        solver = flopt.Solver("ScipyMilpSearch")
        prob.solve(solver, msg=True)

    See Also
    --------
    scipy.optimize.milp
    """

    name = "ScipyMilpSearch"
    can_solve_problems = {
        "Variable": VariableType.Number,
        "Objective": ExpressionType.Linear,
        "Constraint": ExpressionType.Linear,
    }

    def search(self, solution, *args):
        self.start_build()

        # lp structure
        lp = LpStructure.fromFlopt(
            self.prob,
            x=VariableArray(solution.getVariables()),
            option="all_neq",
        )

        # bounds
        lbs = [_lb if not np.isnan(_lb) else -np.inf for _lb in lp.lb]
        ubs = [_ub if not np.isnan(_ub) else np.inf for _ub in lp.ub]
        bounds = scipy_optimize.Bounds(lbs, ubs)

        # integrality
        integrality = [var.type() != VariableType.Continuous for var in lp.x]

        # constraints (lp.G x <= lp.h)
        has_constraints = lp.G is not None
        lb = np.full_like(lp.h, -np.inf)
        if has_constraints:
            constraints = scipy_optimize.LinearConstraint(lp.G, lb, lp.h)
        else:
            constraints = None

        self.end_build()

        # options
        options = {"disp": self.msg, "time_limit": self.timelimit - self.build_time}

        # search
        res = scipy_optimize.milp(
            c=lp.c,
            constraints=constraints,
            integrality=integrality,
            bounds=bounds,
            options=options,
        )

        # res.status =  0: Optimal solution found.
        #               1: Iteration or time limit reached.
        #               2: Problem is infeasible.
        #               3: Problem is unbounded.
        #               4: Other; see message for details.
        if res.status == 0:
            solution.setValuesFromArray(res.x)
            self.registerSolution(solution)
            return SolverTerminateState.Normal
        elif res.status == 1:
            return SolverTerminateState.Timelimit
        elif res.status == 2:
            return SolverTerminateState.Infeasible
        elif res.status == 3:
            return SolverTerminateState.Unbounded
        else:
            return SolverTerminateState.Abnormal

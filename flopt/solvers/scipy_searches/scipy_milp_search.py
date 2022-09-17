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

    See Also
    --------
    scipy.optimize.milp

    Returns
    -------
    status : int
        status of solver
    """

    name = "ScipyMilpSearch"
    can_solve_problems = {
        "Variable": VariableType.Number,
        "Objective": ExpressionType.Linear,
        "Constraint": ExpressionType.Linear,
    }

    def search(self):
        self.start_build()

        var_names = [var.name for var in self.solution]

        # lp structure
        lp = LpStructure.fromFlopt(
            self.prob,
            x=VariableArray(self.solution.getVariables()),
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
        if has_constraints:
            constraints = scipy_optimize.LinearConstraint(
                lp.G, np.full_like(lp.h, -np.inf), lp.h
            )
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
            for var, value in zip(self.solution, res.x):
                var.setValue(value)

            # if solution is better thatn incumbent, then update best solution
            self.registerSolution(self.solution)
            return SolverTerminateState.Normal
        elif res.status == 1:
            return SolverTerminateState.Timelimit
        elif res.status == 2:
            return SolverTerminateState.Infeasible
        elif res.status == 3:
            return SolverTerminateState.Unbounded
        else:
            return SolverTerminateState.Abnormal

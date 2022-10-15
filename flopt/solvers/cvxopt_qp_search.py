from cvxopt import matrix, solvers

from flopt.solvers.base import BaseSearch
from flopt.convert import QpStructure
from flopt.error import SolverError
from flopt.constants import VariableType, ExpressionType, SolverTerminateState
from flopt.env import setup_logger


logger = setup_logger(__name__)


class CvxoptQpSearch(BaseSearch):
    """API of CVXOPT.qp Solver
    https://cvxopt.org/userguide/coneprog.html#quadratic-programming

    Parameters
    ----------
    n_trial : int
        max iteration

    Examples
    --------

    .. code-block:: python

        import flopt

        x = flopt.Variable("x", lowBound=-1, upBound=1, cat="Continuous")
        y = flopt.Variable("y", lowBound=-1, upBound=1, cat="Continuous")

        prob = flopt.Problem()
        prob += 2*x*x + x*y + y*y + x + y
        prob += x >= 0
        prob += y >= 0
        prob += x + y == 1

        solver = flopt.Solver("CvxoptQpSearch")
        status, log = prob.solve(solver, msg=True)

        print("obj =", flopt.Value(prob.obj))
        print("x =", flopt.Value(x))
        print("y =", flopt.Value(y))
        >>> obj = 1.8750000000000002
        >>> x = 0.2500000152449024
        >>> y = 0.7499999847550975

    """

    name = "CvxoptQpSearch"
    can_solve_problems = {
        "Variable": VariableType.Continuous,
        "Objective": ExpressionType.Quadratic,
        "Constraint": ExpressionType.Linear,
    }

    def __init__(self):
        super().__init__()
        self.n_trial = None

    def search(self, solution, *args):
        self.start_build()
        qp = QpStructure.fromFlopt(self.prob).boundsToNeq()
        if qp.isLp():
            sol = self.search_lp(qp.toLp())
        else:
            sol = self.search_qp(qp)

        # fetch solution
        for var, value in zip(qp.x, sol["x"]):
            solution.setValue(var.name, value)

        # update best solution if needed
        self.registerSolution(solution)

        return SolverTerminateState.Normal

    def search_qp(self, qp):

        qp = qp.boundsToNeq()
        Q = matrix(qp.Q)
        c = matrix(qp.c)
        G = matrix(qp.G) if qp.G is not None else None
        h = matrix(qp.h) if qp.h is not None else None
        A = matrix(qp.A) if qp.A is not None else None
        b = matrix(qp.b) if qp.b is not None else None

        # settings
        solvers.options["show_progress"] = self.msg
        if self.n_trial is not None:
            solvers.options["maxiters"] = self.n_trial
        elif "maxiters" in solvers.options:
            del solvers.options["maxiters"]

        self.end_build()

        # solve
        try:
            sol = solvers.qp(Q, c, G, h, A, b)
        except ValueError as e:
            logger.warning(e)
            if G is not None and h is not None:
                G, h = 2 * G, 2 * h
            elif A is not None and b is not None:
                A, b = 2 * A, 2 * b
            else:
                raise SolverError(e)
            try:
                # resolve
                sol = solvers.qp(Q, c, G, h, A, b)
            except Exception as e:
                logger.error(e)
                raise SolverError(e)
        except Exception as e:
            logger.error(e)
            raise SolverError(e)

        return sol

    def search_lp(self, lp):

        c = matrix(lp.c)
        G = matrix(lp.G) if lp.G is not None else None
        h = matrix(lp.h) if lp.h is not None else None
        A = matrix(lp.A) if lp.A is not None else None
        b = matrix(lp.b) if lp.b is not None else None

        # settings
        solvers.options["show_progress"] = self.msg
        if self.n_trial is not None:
            solvers.options["maxiters"] = self.n_trial
        elif "maxiters" in solvers.options:
            del solvers.options["maxiters"]

        self.end_build()

        # solve
        sol = solvers.lp(c, G, h, A, b)
        return sol

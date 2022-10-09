import numpy as np

from amplify import IsingPoly, gen_symbols, Solver, decode_solution
from amplify.constraint import equal_to, greater_equal, less_equal
from amplify.client import FixstarsClient

from flopt.solvers.base import BaseSearch
from flopt.constants import (
    VariableType,
    ExpressionType,
    ConstraintType,
    SolverTerminateState,
)
from flopt.env import setup_logger


logger = setup_logger(__name__)


class AmplifySearch(BaseSearch):
    """API of Amplify Solver (https://amplify.fixstars.com/en/docs/index.html)

    Parameters
    ----------
    timelimit : float or int
        time limit
    token : str
        user token

    Examples
    --------

    AmplifySearch can solve the problem whose variables are Spin

    .. code-block:: python

        from flopt import Variable, Problem

        x = Variable('x', cat='Spin')
        y = Variable('y', cat='Spin')

        prob = Problem()
        prob += 1 - x * y - x
        prob += x + y >= 0

        print(prob.show())
        >>> Name: None
        >>>   Type         : Problem
        >>>   sense        : minimize
        >>>   objective    : 1-(x*y)-x
        >>>   #constraints : 1
        >>>   #variables   : 2 (Spin 2)
        >>>
        >>>   C 0, name None, x+y >= 0

    .. code-block:: python

        from flopt import Solver

        solver = Solver('AmplifySearch')
        solver.setParams(token="xxx")  # your token
        prob.solve(solver, msg=True)

        print()
        print('obj =', Value(prob.obj))
        print('x =', Value(x))
        print('y =', Value(y))
        >>> obj = -1
        >>> x = 1
        >>> y = 1

    In the case, the problem includes the binary variables,
    you should convert them to spin variables.

    .. code-block:: python

        from flopt import Variable, Problem

        x = Variable('x', cat='Binary')
        y = Variable('y', cat='Binary')

        prob = Problem()
        prob += (1 - x * y - x).toSpin()
        prob += (x + y >= 0).toSpin()

        print(prob.show())
        >>> Name: None
        >>>   Type         : Problem
        >>>   sense        : minimize
        >>>   objective    : -0.25*(x_s*y_s)-(0.75*x_s)-(0.25*y_s)+0.25
        >>>   #constraints : 1
        >>>   #variables   : 2 (Spin 2)
        >>>
        >>>   C 0, name None, 0.5*x_s+(0.5*y_s)+1.0 >= 0
    """

    name = "AmplifySearch"
    can_solve_problems = {
        "Variable": VariableType.Spin,
        "Objective": ExpressionType.Quadratic,
        "Constraint": ExpressionType.Linear,
    }

    def __init__(self):
        super().__init__()
        self.timelimit = 1
        self.token = None

    def search(self, solution, objective, constraints):
        assert (
            self.token is not None
        ), f'token is None, set token as .solve(..., token="xxx")'

        self.start_build()

        x = self.prob.getVariables()
        s = gen_symbols(IsingPoly, len(x))
        np_s = np.array(gen_symbols(IsingPoly, len(x)), dtype=object)

        # objective function
        ising = objective.toIsing()
        f = -np_s.T.dot(ising.J).dot(np_s) - ising.h.T.dot(np_s) + ising.C

        # constraints
        for const in constraints:
            ising = const.expression.toIsing()
            g = np_s.T.dot(ising.J).dot(np_s) - ising.h.T.dot(np_s) + ising.C
            if const.type() == ConstraintType.Eq:
                f += equal_to(g, 0)
            else:  # ConstraintType.Le
                f += less_equal(g, 0)

        self.end_build()

        # solve
        client = FixstarsClient()  # Fixstars Optigan
        client.parameters.timeout = int(1000.0 * (self.timelimit - self.build_time))
        client.token = self.token

        result = Solver(client).solve(f)

        for amplify_solution in list(result)[::-1]:
            # fetch solution
            values = decode_solution(s, amplify_solution.values)
            solution.setValuesFromArray(values)

            # update best solution if needed
            self.registerSolution(solution)

        return SolverTerminateState.Normal

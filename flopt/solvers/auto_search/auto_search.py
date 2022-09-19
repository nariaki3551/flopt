import inspect

from flopt.solvers.base import BaseSearch
from flopt.solvers.auto_search.selector import (
    mip,
    ising,
    qp,
    permutation,
    nonlinear,
    nonlinear_mip,
    MipSelector,
    IsingSelector,
    QpSelector,
    PermutationSelector,
    NonlinearSelector,
    NonlinearMipSelector,
    BaseSelector,
    ModelNotFound,
)
from flopt.constants import VariableType, ExpressionType
import flopt.error
from flopt.env import setup_logger

logger = setup_logger(__name__)


class AutoSearch(BaseSearch):
    """Auto Solver Selector

    This automatically selects and runs solver according to the problem and settings.

    .. code-block:: python

        from flopt import Variable, Problem, Solver

        # Variables
        a = Variable('a', lowBound=0, upBound=1, cat='Integer')
        b = Variable('b', lowBound=1, upBound=2, cat='Continuous')
        c = Variable('c', lowBound=1, upBound=3, cat='Continuous')

        prob = Problem(name='Test')
        prob += 2*(3*a+b)*c**2+3

    Then, we use Solver(algo='auto') and solve.

    .. code-block:: python

        solver = Solver(algo='auto')
        solver.setParams({'timelimit': 10})
        prob.solve(solver, msg=True)

        >>> Welcome to the flopt Solver
        >>> Version 0.2
        >>> Date: May 30, 2020
        >>>
        >>> Algorithm: OptunaCmaEsSearch
        >>> Params: {'timelimit': 10}

    See the log, you can see the RandomSearch algorithm is used for this problem.
    Executing .select(), we can check which solver will be select.

    .. code-block:: python

        solver = Solver(algo='auto')
        solver.setParams({'timelimit': 10})
        solver = solver.select(prob)
        print(solver.name)
        >>> OptunaCmaEsSearch

    Selected solver will be changed by the problem and setting to solve.

    .. code-block:: python

        solver = Solver(algo='auto')
        solver.setParams({'timelimit': 3})
        solver = solver.select(prob)
        print(solver.name)
        >>> RandomSearch

    """

    name = "auto"
    can_solve_problems = {
        "Variable": VariableType.Any,
        "Objective": ExpressionType.Any,
        "Constraint": ExpressionType.Any,
    }

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
        from flopt import Solver, Solver_list

        return any(
            Solver(algo=algo).available(prob, verbose)
            for algo in (set(Solver_list()) - {"auto"})
        )

    def select(self, prob):
        """select solver

        Parameters
        ----------
        prob : Problem
            problem
        """
        from flopt import Solver

        problem_type = prob.toProblemType()
        selector = self.getSelector(problem_type)
        algo = selector(prob, self)
        solver = Solver(algo=algo)

        # set params
        attrobjs = [
            (attr, obj)
            for (attr, obj) in inspect.getmembers(self)
            if not callable(obj)
            and attr[:2] != "__"
            and attr[-2:] != "__"
            and attr != "name"
        ]
        for attr, obj in attrobjs:
            setattr(solver, attr, obj)

        return solver

    def getSelector(self, problem_type):
        def check(problem_type, problem_class):
            return (
                problem_type["Variable"].expand() <= problem_class["Variable"].expand()
                and problem_type["Objective"].expand()
                <= problem_class["Objective"].expand()
                and problem_type["Constraint"].expand()
                <= problem_class["Constraint"].expand()
            )

        try:
            if check(problem_type, mip):
                return MipSelector()
            elif check(problem_type, ising):
                return IsingSelector()
            elif check(problem_type, qp):
                return QpSelector()
            elif check(problem_type, permutation):
                return PermutationModel()
            elif check(problem_type, nonlinear):
                return NonlinearSelector()
            elif check(problem_type, nonlinear_mip):
                return NonlinearMipSelector()
        except ModelNotFound as e:
            logger.warning(e)
            return BaseSelector()
        return BaseSelector()

    def solve(self, solution, prob, *args, **kwargs):
        """
        select solver and solve the problem of (solution, obj)

        Parameters
        ----------
        solution : Solution
            solution object
        prob : Problem
            problem

        Returns
        -------
        status, Log
        """
        solver = self.select(prob)
        return solver.solve(solution, prob, *args, **kwargs)

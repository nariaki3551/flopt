import inspect

from flopt.solvers.base import BaseSearch
import flopt.constants
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
    def __init__(self):
        super().__init__()
        self.name = 'AutoSearch'


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
        from flopt import Solver, Solver_list
        return any(Solver(algo=algo).available(prob)
                for algo in (set(Solver_list()) - {'auto'}) )


    def select(self, prob):
        """select solver

        Parameters
        ----------
        prob : Problem
            problem
        """
        from flopt import Solver

        if self.timelimit < 1:
            algo_lists = [
                '2-Opt',
                'RandomSearch',
                'ScipySearch',
                'HyperoptTPESearch',
                'SFLA',
                'OptunaCmaEsSearch',
                'OptunaTPESearch',
                'PulpSearch',
                'CvxoptQpSearch',
                'ScipyLpSearch',
            ]
        if self.timelimit < 5:
            algo_lists = [
                '2-Opt',
                'RandomSearch',
                'ScipySearch',
                'SFLA',
                'OptunaCmaEsSearch',
                'HyperoptTPESearch',
                'OptunaTPESearch',
                'PulpSearch',
                'CvxoptQpSearch',
                'ScipyLpSearch',
            ]
        elif self.timelimit < 30:
            algo_lists = [
                '2-Opt',
                'OptunaCmaEsSearch',
                'RandomSearch',
                'ScipySearch',
                'OptunaTPESearch',
                'HyperoptTPESearch',
                'SFLA',
                'PulpSearch',
                'CvxoptQpSearch',
                'ScipyLpSearch',
            ]
        else:
            algo_lists = [
                '2-Opt',
                'OptunaCmaEsSearch',
                'SFLA',
                'ScipySearch',
                'RandomSearch',
                'OptunaTPESearch',
                'HyperoptTPESearch',
                'PulpSearch',
                'CvxoptQpSearch',
                'ScipyLpSearch',
            ]

        for _algo in algo_lists:
            if Solver(algo=_algo).available(prob):
                algo = _algo
                break
        else:
            raise flopt.error.SolverError

        solver = Solver(algo=algo)
        # set params
        attrobjs = [
            (attr, obj) for (attr, obj) in inspect.getmembers(self)
            if not callable(obj) and attr[:2] != "__" and attr[-2:] != "__" and attr != 'name'
        ]
        for attr, obj in attrobjs:
            setattr(solver, attr, obj)

        return solver


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



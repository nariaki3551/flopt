from flopt.solvers.sequential_update_searches import(
    SequentialUpdateSearch,
    RandomSearch,
    TwoOpt,
)
from flopt.solvers.scipy_searches import (
    ScipySearch,
    ScipyLpSearch,
)
from flopt.solvers.optuna_searches import (
    OptunaSearch,
    OptunaTPESearch,
    OptunaCmaEsSearch
)
from flopt.solvers.hyperopt_search import HyperoptTPESearch
from flopt.solvers.swarm_intelligence_searches import ShuffledFrogLeapingSearch
from flopt.solvers.pulp_search import PulpSearch
from flopt.solvers.cvxopt_qp_search import CvxoptQpSearch
from flopt.solvers.amplify_search import AmplifySearch
from flopt.solvers.auto_search import AutoSearch


algos = {
    'RandomSearch'     : RandomSearch,
    '2-Opt'            : TwoOpt,
    'OptunaTPESearch'  : OptunaTPESearch,
    'OptunaCmaEsSearch': OptunaCmaEsSearch,
    'HyperoptTPESearch': HyperoptTPESearch,
    'SFLA'             : ShuffledFrogLeapingSearch,
    'PulpSearch'       : PulpSearch,
    'ScipySearch'      : ScipySearch,
    'ScipyLpSearch'    : ScipyLpSearch,
    'CvxoptQpSearch'   : CvxoptQpSearch,
    'AmplifySearch'    : AmplifySearch,
    'auto'             : AutoSearch,
}


def Solver(algo='RandomSearch'):
    """
    Obtain Solver object.

    Parameters
    ----------
    algo : str
      algorithm name

    Returns
    -------
    Solver object
       return Solver
    """
    return algos[algo]()


def Solver_list():
    """
    Obtain useable solver list

    Returns
    -------
    list
      return list of algorithm names
    """
    return list(algos)


def allAvailableSolvers(prob):
    """Obtain all available solvers to solve the problem

    Parameters
    ----------
    prob : Problem
        problem

    Returns
    -------
    list of algorithm name

    Examples
    --------


    .. code-block:: python

        import flopt
        from flopt import Variable, Problem, CustomExpression

        # Problem without constraint
        a = Variable('a', 0, 1, 'Integer')
        b = Variable('b', 1, 2, 'Continuous')
        c = Variable('c', 1, 3, 'Continuous')
        prob_linear = Problem(name='Test')
        prob_linear += a + b + c

        # Problem with constraint
        prob_with_const = Problem(name='TestC')
        prob_with_const += a + b + c
        prob_with_const += a + b >= 2

        # Non-Linear problem
        prob_nonlinear = Problem('Non-Linear')
        prob_nonlinear += a*b*c
        prob_nonlinear += a + b >= 2

        # Permutation Problem
        p = Variable('p', 0, 4, 'Permutation')
        prob_perm = Problem('TestP')
        def obj(p):
            return p[-1] - p[0]
        prob_perm +=  CustomExpression(obj, [p])

        print(flopt.allAvailableSolvers(prob_linear)
        >>> ['RandomSearch',
        >>> 'OptunaTPESearch',
        >>> 'OptunaCmaEsSearch',
        >>> 'HyperoptTPESearch',
        >>> 'SFLA',
        >>> 'PulpSearch',
        >>> 'ScipySearch']

        print(flopt.allAvailableSolvers(prob_with_const))
        >>> ['PulpSearch', 'ScipySearch']

        print(flopt.allAvailableSolvers(prob_nonlinear))
        >>> ['ScipySearch']

        print(flopt.allAvailableSolvers(prob_perm))
        >>> ['RandomSearch', '2-Opt']
    """
    available_solvers = [
        algo for algo in Solver_list()
        if Solver(algo=algo).available(prob)
    ]
    return available_solvers


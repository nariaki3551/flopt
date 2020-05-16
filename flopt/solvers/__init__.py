from flopt.solvers.sequential_update_searches import(
    SequentialUpdateSearch,
    RandomSearch,
    TwoOpt
)
from flopt.solvers.optuna_searches import (
    OptunaSearch,
    OptunaTPESearch,
    OptunaCmaEsSearch
)
from flopt.solvers.hyperopt_search import HyperoptTPESearch
from flopt.solvers.swarm_intelligence_searches import ShuffledFrogLeapingSearch
from flopt.solvers.pulp_search import PulpSearch
from flopt.solvers.scipy_search import ScipySearch

algos = {
    'RandomSearch'     : RandomSearch,
    '2-Opt'            : TwoOpt,
    'OptunaTPESearch'  : OptunaTPESearch,
    'OptunaCmaEsSearch': OptunaCmaEsSearch,
    'HyperoptTPESearch': HyperoptTPESearch,
    'SFLA'             : ShuffledFrogLeapingSearch,
    'PulpSearch'       : PulpSearch,
    'ScipySearch'      : ScipySearch,
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

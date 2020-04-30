from .sequential_update_searches import(
    SequentialUpdateSearch,
    RandomSearch,
    TwoOpt
)
from .optuna_searches import (
    OptunaSearch,
    OptunaTPESearch,
    OptunaCmaEsSearch
)
from .hyperopt_search import HyperoptTPESearch
from .swarm_intelligence_searches import ShuffledFrogLeapingSearch

algos = {
    'RandomSearch'     : RandomSearch,
    '2-Opt'            : TwoOpt,
    'OptunaTPESearch'  : OptunaTPESearch,
    'OptunaCmaEsSearch': OptunaCmaEsSearch,
    'HyperoptTPESearch': HyperoptTPESearch,
    'SFLA'             : ShuffledFrogLeapingSearch
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

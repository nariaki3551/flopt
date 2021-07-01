VERSION = '0.2'
DATE = 'May 30, 2020'

# termination state
SOLVER_NORMAL_TERMINATE    = 0
SOLVER_TIMELIMIT_TERMINATE = 1
SOLVER_INTERRUPT_TERMINATE = 2
SOLVER_ABNORMAL_TERMINATE  = 3

# error handlings
class SolverError(Exception):
    pass

class ModelingError(SolverError):
    """error which is occurred with modeling in Solver"""
    pass

from flopt.env import Environment

env = Environment()

from flopt.variable import Variable
from flopt.expression import CustomExpression
from flopt.problem import Problem
from flopt.solvers import Solver, Solver_list, allAvailableSolvers
from flopt.solution import Solution
from flopt.utils import Sum, Prod, Dot, Value, Sqnorm, Norm

# performance
import flopt.performance

# visualize
from flopt.utils import get_dot_graph

# constants
import flopt.constants

VarContinuous = flopt.constants.VariableType.Continuous
VarInteger = flopt.constants.VariableType.Integer
VarBinary = flopt.constants.VariableType.Binary
VarSpin = flopt.constants.VariableType.Spin
VerPermutation = flopt.constants.VariableType.Permutation

Minimize = flopt.constants.OptimizationType.Minimize
Maximize = flopt.constants.OptimizationType.Maximize

SolverTerminateState = flopt.constants.SolverTerminateState

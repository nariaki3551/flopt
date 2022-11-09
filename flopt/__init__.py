from flopt.env import Environment

env = Environment()

from flopt.variable import Variable
from flopt.container import FloptNdarray as variable_ndarray
from flopt.expression import CustomExpression
from flopt.problem import Problem
from flopt.solvers import (
    Solver,
    Solver_list,
    allAvailableSolvers,
    estimate_problem_type_info,
)
from flopt.solution import Solution

# performance
import flopt.performance

# visualize
from flopt.utils import get_dot_graph

# constants
import flopt.constants

# operations
from flopt.utils import Sum
from flopt.utils import Sum as sum
from flopt.utils import Prod
from flopt.utils import Prod as prod
from flopt.utils import Dot
from flopt.utils import Dot as dot
from flopt.utils import Norm
from flopt.utils import Norm as norm
from flopt.utils import Sqnorm
from flopt.utils import Sqnorm as sqnorm
from flopt.utils import Value
from flopt.utils import sqrt
from flopt.utils import exp
from flopt.utils import cos
from flopt.utils import sin
from flopt.utils import tan
from flopt.utils import log
from flopt.utils import abs
from flopt.utils import floor
from flopt.utils import ceil

VarContinuous = flopt.constants.VariableType.Continuous
VarInteger = flopt.constants.VariableType.Integer
VarBinary = flopt.constants.VariableType.Binary
VarSpin = flopt.constants.VariableType.Spin
VerPermutation = flopt.constants.VariableType.Permutation

Minimize = flopt.constants.OptimizationType.Minimize
Maximize = flopt.constants.OptimizationType.Maximize

SolverTerminateState = flopt.constants.SolverTerminateState

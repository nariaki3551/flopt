import enum

import numpy as np

VERSION = "0.5.4"
DATE = "September 1, 2022"


# number classes
number_classes = (int, float, np.number)


# array classes
array_classes = (list, tuple, np.ndarray)


# numpy floating point
np_float = np.float64


# termination state
class SolverTerminateState(enum.IntEnum):
    Normal = 0
    Timelimit = 1
    Lowerbound = 2
    Interrupt = 3
    Infeasible = 4
    Unbounded = 5
    Abnormal = 6

    def __str__(self):
        return self.name


# variable type
class VariableType(enum.IntEnum):
    Continuous = 100
    Integer = 101
    Binary = 102
    Spin = 103
    Permutation = 104

    def __str__(self):
        return self.name


# expression type
class ExpressionType(enum.IntEnum):
    Normal = 200
    Custom = 201
    Const = 202
    Sum = 203
    Prod = 204

    def __str__(self):
        return self.name


# expression type
class ConstraintType(enum.IntEnum):
    Le = 300
    Eq = 301

    def __str__(self):
        return self.name


# optimization type
class OptimizationType(enum.IntEnum):
    Minimize = 400
    Maximize = 401

    def __str__(self):
        return self.name

import enum

import numpy as np

VERSION = "0.5.5"
DATE = "October 15, 2022"

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
    Error = 7

    def __str__(self):
        sts = self.__class__
        status_str = {
            sts.Normal: "Normal termination",
            sts.Timelimit: "Timelimit termination",
            sts.Lowerbound: "Lowerbound termination",
            sts.Interrupt: "Ctrl-C termination",
            sts.Unbounded: "Found unbounded",
            sts.Infeasible: "Found infeasibility",
            sts.Abnormal: "Abnormal termination",
            sts.Error: "Error",
        }
        return status_str[self]


# variable type
class VariableType(enum.IntEnum):
    Continuous = 100
    Integer = 101
    Binary = 102
    Spin = 103
    Permutation = 104
    Any = 105  # Number | Permutation
    Number = 106  # Continuous | Integer | Binary | Spin

    def __str__(self):
        return self.name

    def expand(self):
        vt = self.__class__
        if self == vt.Binary:
            return {vt.Binary, vt.Spin}
        elif self == vt.Spin:
            return {vt.Binary, vt.Spin}
        elif self == vt.Number:
            return {vt.Continuous, vt.Integer, vt.Binary, vt.Spin}
        elif self == vt.Any:
            return vt.Number.expand() | {vt.Permutation}
        return {self}


# expression type
class ExpressionType(enum.IntEnum):
    Unknown = 200
    Any = 201
    Linear = 202
    Quadratic = 203
    Polynomial = 204
    Nonlinear = 205
    Permutation = 206
    BlackBox = 207
    Non = 208

    def __str__(self):
        return self.name

    def expand(self):
        et = self.__class__
        if self == et.Any:
            return {
                et.Unknown,
                et.Linear,
                et.Quadratic,
                et.Polynomial,
                et.Nonlinear,
                et.Permutation,
                et.BlackBox,
                et.Non,
            }
        elif self == et.Linear:
            return {et.Linear, et.Non}
        elif self == et.Quadratic:
            return {et.Linear, et.Quadratic, et.Non}
        elif self == et.Polynomial:
            return {et.Linear, et.Quadratic, et.Polynomial, et.Non}
        elif self == et.Permutation:
            return {et.Permutation, et.Non}
        elif self == et.BlackBox:
            return {et.Permutation, et.BlackBox, et.Non}
        elif self == et.Nonlinear:
            return {
                et.Linear,
                et.Quadratic,
                et.Polynomial,
                et.Nonlinear,
                et.Non,
            }
        return {self, et.Non}


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


# problem type
class ProblemType(enum.IntEnum):
    BlackBox = 500
    MILP = 501  # Mixed Integer Liear Programming
    QP = 502  # Quadratic Programming
    Ising = 503  # Ising
    QUBO = 504
    Permutation = 505

import enum

VERSION = '0.4'
DATE = 'August 12, 2021'


# termination state
class SolverTerminateState(enum.IntEnum):
    Normal      = enum.auto()
    Timelimit   = enum.auto()
    Interrupt   = enum.auto()
    Abnormal    = enum.auto()


# variable type
class VariableType(enum.IntEnum):
    Continuous  = enum.auto()
    Integer     = enum.auto()
    Binary      = enum.auto()
    Spin        = enum.auto()
    Permutation = enum.auto()


# expression type
class ExpressionType(enum.IntEnum):
    Normal  = enum.auto()
    Custom  = enum.auto()
    Const   = enum.auto()

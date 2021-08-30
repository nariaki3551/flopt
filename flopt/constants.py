import enum

VERSION = '0.4'
DATE = 'August 12, 2021'


# termination state
class SolverTerminateState(enum.IntEnum):
    Normal      = 0
    Timelimit   = 1
    Interrupt   = 2
    Abnormal    = 3

    def __str__(self):
        return self.name



# variable type
class VariableType(enum.IntEnum):
    Continuous  = 100
    Integer     = 101
    Binary      = 102
    Spin        = 103
    Permutation = 104

    def __str__(self):
        return self.name



# expression type
class ExpressionType(enum.IntEnum):
    Normal  = 1000
    Custom  = 1001
    Const   = 1002

    def __str__(self):
        return f'ExpressionType.{self.name}'

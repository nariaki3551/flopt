from flopt import Variable
from math import sin, sqrt

def create_objective(*args, **kwargs):
    def obj(x):
        x1, x2 = x
        return -(x2+47)*sin(sqrt(abs(x2+x1/2+47)))-x1*sin(sqrt(abs(x1-x2-47)))
    return obj

def create_variables(*args, **kwargs):
    variables = [
        Variable(
            name=f'x{i}',
            lowBound=-512,
            upBound=512,
            cat='Continuous'
        )
        for i in [0, 1]
    ]
    return variables

def minimum_obj(*args, **kwargs):
    return -959.6407

from flopt import Variable
from math import sin, pi

def create_objective(*args, **kwargs):
    def obj(x):
        x1, x2 = x
        c1 = sin(3*pi*x1)
        c2 = sin(3*pi*x2)
        c3 = sin(2*pi*x2)
        c4 = (x1-1)*(x1-1)
        c5 = (x2-1)*(x2-1)
        return c1*c1+c4*(1+c2*c2)+c5*(1+c3*c3)
    return obj


def create_variables(*args, **kwargs):
    variables = [
        Variable(
            name=f'x{i}',
            lowBound=-10,
            upBound=10,
            cat='Continuous'
        )
        for i in [0, 1]
    ]
    return variables

def minimum_obj(*args, **kwargs):
    return 0

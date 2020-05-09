from math import exp, sqrt, e, sin, cos, pi
from flopt import Variable

def create_objective(n):
    def obj(x):
        c1 = sum(abs(xi) for xi in x)
        c2 = sum(sin(xi*xi) for xi in x)
        return c1*exp(-c2)
    return obj

def create_variables(n):
    variables = [
        Variable(
            name=f'x{i}',
            lowBound=-2*pi,
            upBound=2*pi,
            cat='Continuous'
        )
        for i in range(n)
    ]
    return variables


def minimum_obj(n):
    return 0

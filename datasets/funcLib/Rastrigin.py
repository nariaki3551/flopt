from math import exp, sqrt, e, cos, pi
from flopt import Variable

def create_objective(n):
    def obj(x):
        return 10*len(x) + sum(xi*xi-10*cos(2*pi*xi) for xi in x)
    return obj

def create_variables(n):
    variables = [
        Variable(
            name=f'x{i}',
            lowBound=-5.12,
            upBound=5.12,
            cat='Continuous'
        )
        for i in range(n)
    ]
    return variables


def minimum_obj(n):
    return 0

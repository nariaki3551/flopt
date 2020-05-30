from math import exp, sqrt, e, cos, pi
from flopt import Variable

def create_objective(n):
    def obj(x):
        c1 = sum(xi*xi for xi in x)
        c2 = 1
        for i, xi in enumerate(x, 1):
            c2 *= cos(xi/sqrt(i))
        return 1 + c1/4000 - c2
    return obj

def create_variables(n):
    variables = [
        Variable(
            name=f'x{i}',
            lowBound=-600,
            upBound=600,
            cat='Continuous'
        )
        for i in range(n)
    ]
    return variables


def minimum_obj(n):
    return 0

from math import exp, sqrt, e, cos, pi
from flopt import Variable

def create_objective(n):
    def obj(x):
        c1 = sum(x)
        c2 = sum(i*xi for i, xi in enumerate(x, 1))
        return c1 + (c2/2)**2 + (c2/2)**4
    return obj

def create_variables(n):
    variables = [
        Variable(
            name=f'x{i}',
            cat='Continuous'
        )
        for i in range(n)
    ]
    return variables


def minimum_obj(n):
    return 0

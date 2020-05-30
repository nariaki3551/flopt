from math import exp, sqrt, e, cos, pi, ceil
from flopt import Variable

def create_objective(n):
    def obj(x):
        n = len(x)
        k = ceil(n/4)
        return sum(xi*xi for xi in x[:k]) + sum(10000*xi*xi for xi in x[k:])
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

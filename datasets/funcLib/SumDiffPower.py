from math import exp, sqrt, e, cos, pi
from flopt import Variable

def create_objective(n):
    def obj(x):
        return sum(abs(xi)**(i+1) for i, xi in enumerate(x, 1))
    return obj

def create_variables(n):
    variables = [
        Variable(
            name=f'x{i}',
            lowBound=-1,
            upBound=1,
            cat='Continuous'
        )
        for i in range(n)
    ]
    return variables


def minimum_obj(n):
    return 0

from flopt import Variable
from math import floor

def create_objective(*args, **kwargs):
    def obj(x):
        return sum(floor(xi) for xi in x)
    return obj

def create_variables(*args, **kwargs):
    variables = [
        Variable(
            name=f'x{i}',
            lowBound=-5.12,
            upBound=5.12,
            cat='Continuous'
        )
        for i in range(5)
    ]
    return variables


def minimum_obj(n):
    return -6*n

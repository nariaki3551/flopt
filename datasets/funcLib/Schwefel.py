from math import exp, sqrt, e, sin, cos, pi
from flopt import Variable

def create_objective(n):
    def obj(x):
        return -sum(xi*sin(sqrt(abs(xi))) for xi in x)
    return obj

def create_variables(n):
    variables = [
        Variable(
            name=f'x{i}',
            lowBound=-500,
            upBound=500,
            cat='Continuous'
        )
        for i in range(n)
    ]
    return variables


def minimum_obj(n):
    return -418.9829*n

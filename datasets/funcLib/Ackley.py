from math import exp, sqrt, e, cos, pi
from flopt import Variable

def create_objective(n):
    def obj(x):
        return 20 - 20*(exp(-0.2*sqrt(sum(xi*xi for xi in x))/len(x))) + e - exp(sum(cos(2*pi*xi) for xi in x)/len(x))
    return obj

def create_variables(n):
    variables = [
        Variable(
            name=f'x{i}',
            lowBound=-32.768,
            upBound=32.768,
            cat='Continuous'
        )
        for i in range(n)
    ]
    return variables


def minimum_obj(n):
    return 0

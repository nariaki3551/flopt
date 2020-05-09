from math import exp, sqrt, e, sin, cos, pi, sin
from flopt import Variable

def create_objective(*args, **kwargs):
    def obj(x):
        m = 10
        fi = lambda i: sin(x[i])*sin(i*x[i]*x[i]/pi)**(2**m)
        return sum(fi(i) for i in range(len(x)))
    return obj

def create_variables(n):
    variables = [
        Variable(
            name=f'x{i}',
            lowBound=0,
            upBound=pi,
            cat='Continuous'
        )
        for i in range(2)
    ]
    return variables


def minimum_obj(n):
    return -1.8013

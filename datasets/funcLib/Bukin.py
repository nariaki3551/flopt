from flopt import Variable
from math import sqrt

def create_objective(*args, **kwargs):
    def obj(x):
        x1, x2 = x
        return 100*(sqrt(abs(x2-0.01*x1*x1)))+0.01*abs(x1+10)
    return obj


def create_variables(*args, **kwargs):
    variables = [
        Variable(
            name=f'x1',
            lowBound=-15,
            upBound=-5,
            cat='Continuous'
        ),
        Variable(
            name=f'x2',
            lowBound=-3,
            upBound=3,
            cat='Continuous'
        )
    ]
    return variables

def minimum_obj(*args, **kwargs):
    return 0

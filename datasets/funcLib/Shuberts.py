from flopt import Variable
from math import cos

def create_objective(*args, **kwargs):
    def obj(x):
        x1, x2 = x
        n = 5
        c1 = sum(i*cos(i+(i+1)*x1) for i in range(1, n+1))
        c2 = sum(i*cos(i+(i+1)*x2) for i in range(1, n+1))
        return c1*c2
    return obj

def create_variables(*args, **kwargs):
    variables = [
        Variable(
            name=f'x1',
            lowBound=-10,
            cat='Continuous'
        ),
        Variable(
            name=f'x2',
            upBound=10,
            cat='Continuous'
        )
    ]
    return variables

def minimum_obj(*args, **kwargs):
    return -186.7309

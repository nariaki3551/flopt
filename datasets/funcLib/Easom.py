from flopt import Variable
from math import cos, exp, pi

def create_objective(*args, **kwargs):
    def obj(x):
        x1, x2 = x
        return -cos(x1)*cos(x2)*exp(-((x1-pi)*(x1-pi)+(x2-pi)*(x2-pi)))
    return obj

def create_variables(*args, **kwargs):
    variables = [
        Variable(
            name=f'x{i}',
            lowBound=-100,
            upBound=100,
            cat='Continuous'
        )
        for i in [0, 1]
    ]
    return variables

def minimum_obj(*args, **kwargs):
    return -1

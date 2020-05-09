from flopt import Variable
from math import sin

def create_objective(*args, **kwargs):
    def obj(x):
        x1, x2 = x
        return 0.5+(sin(x1*x1-x2*x2)**2-0.5)/(1+0.001*(x1*x1+x2*x2))**2
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
    return 0

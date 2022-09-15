from math import sin

import flopt


def create_objective(*args, **kwargs):
    def obj(x):
        x1, x2 = x
        return sin(x1 + x2) + (x1 - x2) * (x1 - x2) - 1.5 * x1 + 2.5 * x2 + 1

    return obj


def create_variables(cat="Continuous", *args, **kwargs):
    variables = [
        flopt.Variable(name=f"x1", lowBound=-1.5, upBound=4, cat=cat),
        flopt.Variable(name=f"x2", lowBound=-3, upBound=4, cat=cat),
    ]
    return variables


def minimum_obj(*args, **kwargs):
    return -1.9133

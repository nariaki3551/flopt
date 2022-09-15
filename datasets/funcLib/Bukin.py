from math import sqrt

import flopt


def create_objective(*args, **kwargs):
    def obj(x):
        x1, x2 = x
        return 100 * (sqrt(abs(x2 - 0.01 * x1 * x1))) + 0.01 * abs(x1 + 10)

    return obj


def create_variables(cat="Continuous", *args, **kwargs):
    variables = [
        flopt.Variable(name=f"x1", lowBound=-15, upBound=-5, cat=cat),
        flopt.Variable(name=f"x2", lowBound=-3, upBound=3, cat=cat),
    ]
    return variables


def minimum_obj(*args, **kwargs):
    return 0

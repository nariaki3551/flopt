from math import cos

import flopt


def create_objective(*args, **kwargs):
    def obj(x):
        x1, x2 = x
        n = 5
        c1 = sum(i * cos(i + (i + 1) * x1) for i in range(1, n + 1))
        c2 = sum(i * cos(i + (i + 1) * x2) for i in range(1, n + 1))
        return c1 * c2

    return obj


def create_variables(cat="Continuous", *args, **kwargs):
    variables = [
        flopt.Variable(name=f"x1", lowBound=-10, cat=cat),
        flopt.Variable(name=f"x2", upBound=10, cat=cat),
    ]
    return variables


def minimum_obj(*args, **kwargs):
    return -186.7309

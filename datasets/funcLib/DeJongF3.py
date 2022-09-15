from math import floor

import flopt


def create_objective(*args, **kwargs):
    def obj(x):
        return sum(floor(xi) for xi in x)

    return obj


def create_variables(cat="Continuous", *args, **kwargs):
    variables = flopt.Variable.array("x", 5, lowBound=-5.12, upBound=5.12, cat=cat)
    return variables


def minimum_obj(n):
    return -6 * n

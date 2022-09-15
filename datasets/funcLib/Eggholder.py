from math import sin, sqrt

import flopt


def create_objective(*args, **kwargs):
    def obj(x):
        x1, x2 = x
        return -(x2 + 47) * sin(sqrt(abs(x2 + x1 / 2 + 47))) - x1 * sin(
            sqrt(abs(x1 - x2 - 47))
        )

    return obj


def create_variables(cat="Continuous", *args, **kwargs):
    variables = flopt.Variable.array("x", 2, lowBound=-512, upBound=512, cat=cat)
    return variables


def minimum_obj(*args, **kwargs):
    return -959.6407

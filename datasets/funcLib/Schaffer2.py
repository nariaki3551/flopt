from math import sin

import flopt


def create_objective(*args, **kwargs):
    def obj(x):
        x1, x2 = x
        return (
            0.5
            + (sin(x1 * x1 - x2 * x2) ** 2 - 0.5)
            / (1 + 0.001 * (x1 * x1 + x2 * x2)) ** 2
        )

    return obj


def create_variables(cat="Continuous", *args, **kwargs):
    variables = flopt.Variable.array("x", 2, lowBound=-100, upBound=100, cat=cat)
    return variables


def minimum_obj(*args, **kwargs):
    return 0

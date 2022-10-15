from math import cos, exp, pi

import flopt


def create_objective(*args, **kwargs):
    def obj(x):
        x1, x2 = x
        return (
            -cos(x1) * cos(x2) * exp(-((x1 - pi) * (x1 - pi) + (x2 - pi) * (x2 - pi)))
        )

    return obj


def create_variables(cat="Continuous", *args, **kwargs):
    variables = flopt.Variable.array("x", 2, lowBound=-100, upBound=100, cat=cat)
    return variables


def minimum_obj(*args, **kwargs):
    return -1

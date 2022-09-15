from math import sin, pi

import flopt


def create_objective(*args, **kwargs):
    def obj(x):
        x1, x2 = x
        c1 = sin(3 * pi * x1)
        c2 = sin(3 * pi * x2)
        c3 = sin(2 * pi * x2)
        c4 = (x1 - 1) * (x1 - 1)
        c5 = (x2 - 1) * (x2 - 1)
        return c1 * c1 + c4 * (1 + c2 * c2) + c5 * (1 + c3 * c3)

    return obj


def create_variables(cat="Continuous", *args, **kwargs):
    variables = flopt.Variable.array(f"x", 2, lowBound=-10, upBound=10, cat=cat)
    return variables


def minimum_obj(*args, **kwargs):
    return 0

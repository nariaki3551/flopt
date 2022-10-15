from math import cos, pi

import flopt


def create_objective(n):
    def obj(x):
        return 10 * len(x) + sum(xi * xi - 10 * cos(2 * pi * xi) for xi in x)

    return obj


def create_variables(n, cat="Continuous"):
    variables = flopt.Variable.array("x", n, lowBound=-5.12, upBound=5.12, cat=cat)
    return variables


def minimum_obj(n):
    return 0

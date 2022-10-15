from math import exp, sin, pi

import flopt


def create_objective(n):
    def obj(x):
        c1 = sum(abs(xi) for xi in x)
        c2 = sum(sin(xi * xi) for xi in x)
        return c1 * exp(-c2)

    return obj


def create_variables(n, cat="Continuous"):
    variables = flopt.Variable.array("x", n, lowBound=-2 * pi, upBound=2 * pi, cat=cat)
    return variables


def minimum_obj(n):
    return 0

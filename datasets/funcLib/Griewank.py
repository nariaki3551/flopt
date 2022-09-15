from math import exp, sqrt, e, cos, pi

import flopt


def create_objective(n):
    def obj(x):
        c1 = flopt.Sqnorm(x)
        c2 = flopt.Prod(cos(xi / sqrt(i)) for i, xi in enumerate(x, 1))
        return 1 + c1 / 4000 - c2

    return obj


def create_variables(n, cat="Continuous"):
    variables = flopt.Variable.array("x", n, lowBound=-600, upBound=600, cat=cat)
    return variables


def minimum_obj(n):
    return 0

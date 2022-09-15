from math import exp, sqrt, e, cos, pi, ceil

import flopt


def create_objective(n):
    def obj(x):
        n = len(x)
        k = ceil(n / 4)
        return flopt.Sqnorm(x[:k]) + 10000 * flopt.Sqnorm(x[k:])

    return obj


def create_variables(n, cat="Continuous"):
    variables = flopt.Variable.array("x", n, lowBound=-5.12, upBound=5.12, cat=cat)
    return variables


def minimum_obj(n):
    return 0

from math import exp, sqrt, e, cos, pi

import flopt


def create_objective(n):
    def obj(x):
        return (
            20
            - 20 * (exp(-0.2 * sqrt(flopt.Sqnorm(x)) / len(x)))
            + e
            - exp(sum(cos(2 * pi * xi) for xi in x) / len(x))
        )

    return obj


def create_variables(n, cat="Continuous"):
    variables = flopt.Variable.array("x", n, lowBound=-5.12, upBound=5.12, cat=cat)
    return variables


def minimum_obj(n):
    return 0

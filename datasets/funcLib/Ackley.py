from math import exp, sqrt, e, cos, pi

import flopt


def create_objective(n):
    def obj(x):
        return (
            20
            - 20 * (exp(-0.2 * sqrt(sum(xi * xi for xi in x)) / len(x)))
            + e
            - exp(sum(cos(2 * pi * xi) for xi in x) / len(x))
        )

    return obj


def create_variables(n):
    variables = flopt.Variable.array(
        "x", n, lowBound=-5.12, upBound=5.12, cat="Continuous"
    )
    return variables


def minimum_obj(n):
    return 0

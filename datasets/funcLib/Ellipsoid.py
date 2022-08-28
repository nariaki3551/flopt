from math import exp, sqrt, e, cos, pi

import flopt


def create_objective(n):
    def obj(x):
        return sum(1000 * (i - 1 / n - 1) * xi for i, xi in enumerate(x, 1))

    return obj


def create_variables(n):
    variables = flopt.Variable.array(
        "x", n, lowBound=-5.12, upBound=5.12, cat="Continuous"
    )
    return variables


def minimum_obj(n):
    return 0

from math import exp, sqrt, e, cos, pi, ceil

import flopt


def create_objective(n):
    def obj(x):
        n = len(x)
        k = ceil(n / 4)
        return flopt.Sum(xi * xi for xi in x[:k]) + flopt.Sum(
            10000 * xi * xi for xi in x[k:]
        )

    return obj


def create_variables(n):
    variables = flopt.Variable.array(
        "x", n, lowBound=-5.12, upBound=5.12, cat="Continuous"
    )
    return variables


def minimum_obj(n):
    return 0

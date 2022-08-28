from math import sqrt, sin

import flopt


def create_objective(n):
    def obj(x):
        return -sum(xi * sin(sqrt(abs(xi))) for xi in x)

    return obj


def create_variables(n):
    variables = flopt.Variable.array(
        "x", n, lowBound=-500, upBound=500, cat="Continuous"
    )
    return variables


def minimum_obj(n):
    return -418.9829 * n

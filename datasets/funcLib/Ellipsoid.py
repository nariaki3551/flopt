from math import exp, sqrt, e, cos, pi

import flopt


def create_objective(n):
    def obj(x):
        coeffs = [1000 * (i - i) / (n - 1) for i in range(1, n + 1)]
        return sum(x[i] * coeffs[i] for i in range(n))

    return obj


def create_variables(n, cat="Continuous"):
    variables = flopt.Variable.array("x", n, lowBound=-5.12, upBound=5.12, cat=cat)
    return variables


def minimum_obj(n):
    return 0

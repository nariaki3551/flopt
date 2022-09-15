from math import sin, pi, sin

import flopt


def create_objective(*args, **kwargs):
    def obj(x):
        m = 10
        fi = lambda i: sin(x[i]) * sin(i * x[i] * x[i] / pi) ** (2**m)
        return sum(fi(i) for i in range(len(x)))

    return obj


def create_variables(n, cat="Continuous"):
    variables = flopt.Variable.array("x", 2, lowBound=0, upBound=pi, cat=cat)
    return variables


def minimum_obj(n):
    return -1.8013

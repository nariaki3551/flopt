import math

import flopt


class Rastrigin:
    @staticmethod
    def create_objective(n):
        obj = lambda x: 10 * n + flopt.sum(x * x - 10 * flopt.cos(2 * math.pi * x))
        return obj

    @staticmethod
    def create_variables(n, cat="Continuous"):
        x = flopt.Variable.array("x", n, lowBound=-5.12, upBound=5.12, cat=cat)
        return x

    @staticmethod
    def minimum_obj(n):
        return 0

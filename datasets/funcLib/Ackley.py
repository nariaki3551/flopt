import math

import flopt


class Ackley:
    @staticmethod
    def create_objective(n):
        obj = (
            lambda x: 20
            - 20 * (flopt.exp(-0.2 * flopt.norm(x)) / n)
            + math.e
            - flopt.exp(flopt.sum(flopt.cos(2 * math.pi * x)) / n)
        )
        return obj

    @staticmethod
    def create_variables(n, cat="Continuous"):
        x = flopt.Variable.array("x", n, lowBound=-5.12, upBound=5.12, cat=cat)
        return x

    @staticmethod
    def minimum_obj(n):
        return 0

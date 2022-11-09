import math

import flopt


class Easom:
    @staticmethod
    def create_objective(*args, **kwargs):
        obj = lambda x: -flopt.prod(flopt.cos(x)) * flopt.exp(
            -flopt.sqnorm(x - math.pi)
        )
        return obj

    @staticmethod
    def create_variables(cat="Continuous", *args, **kwargs):
        x = flopt.Variable.array("x", 2, lowBound=-100, upBound=100, cat=cat)
        return x

    @staticmethod
    def minimum_obj(*args, **kwargs):
        return -1

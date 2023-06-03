import math

import flopt


class Michalewicz:
    @staticmethod
    def create_objective(*args, **kwargs):
        obj = lambda x: -flopt.sum(
            flopt.sin(x[i]) * flopt.sin((i + 1) * x[i] ** 2 / math.pi) ** (2**10)
            for i in range(2)
        )
        return obj

    @staticmethod
    def create_variables(n, cat="Continuous"):
        x = flopt.Variable.array("x", 2, lowBound=0, upBound=math.pi, cat=cat)
        return x

    @staticmethod
    def minimum_obj(*args, **kwargs):
        return -1.8013

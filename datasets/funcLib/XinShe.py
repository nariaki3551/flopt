import math

import flopt


class XinShe:
    @staticmethod
    def create_objective(n):
        def obj(x):
            c1 = flopt.sum(flopt.abs(x))
            c2 = flopt.sum(flopt.sin(x * x))
            return c1 * flopt.exp(-c2)

        return obj

    @staticmethod
    def create_variables(n, cat="Continuous"):
        x = flopt.Variable.array(
            "x", n, lowBound=-2 * math.pi, upBound=2 * math.pi, cat=cat
        )
        return x

    @staticmethod
    def minimum_obj(n):
        return 0

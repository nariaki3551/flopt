import math

import flopt


class Ktable:
    @staticmethod
    def create_objective(n):
        def obj(x):
            k = math.ceil(n / 4)
            return flopt.sqnorm(x[:k]) + 10000 * flopt.sqnorm(x[k:])

        return obj

    @staticmethod
    def create_variables(n, cat="Continuous"):
        x = flopt.Variable.array("x", n, lowBound=-5.12, upBound=5.12, cat=cat)
        return x

    @staticmethod
    def minimum_obj(n):
        return 0

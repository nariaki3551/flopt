import math

import flopt


class Levi:
    @staticmethod
    def create_objective(*args, **kwargs):
        def obj(x):
            x1, x2 = x
            c1 = flopt.sin(3 * math.pi * x1)
            c2 = flopt.sin(3 * math.pi * x2)
            c3 = flopt.sin(2 * math.pi * x2)
            c4 = (x1 - 1) * (x1 - 1)
            c5 = (x2 - 1) * (x2 - 1)
            return c1 * c1 + c4 * (1 + c2 * c2) + c5 * (1 + c3 * c3)

        return obj

    @staticmethod
    def create_variables(cat="Continuous", *args, **kwargs):
        x = flopt.Variable.array(f"x", 2, lowBound=-10, upBound=10, cat=cat)
        return x

    @staticmethod
    def minimum_obj(*args, **kwargs):
        return 0

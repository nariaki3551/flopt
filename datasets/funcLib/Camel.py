import flopt


class Camel:
    @staticmethod
    def create_objective(*args, **kwargs):
        def obj(x):
            x1, x2 = x
            c1 = 2 * x1 * x1 - 1.05 * x1**4 + x1**6
            c2 = 6 + x1 * x2 + x2 * x2
            return c1 / c2

        return obj

    @staticmethod
    def create_variables(cat="Continuous", *args, **kwargs):
        x = flopt.Variable.array("x", 2, lowBound=-5, upBound=5, cat=cat)
        return x

    @staticmethod
    def minimum_obj(*args, **kwargs):
        return 0

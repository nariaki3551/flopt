import flopt


class Matyas:
    @staticmethod
    def create_objective(*args, **kwargs):
        obj = lambda x: 0.26 * (flopt.sqnorm(x) - 0.48 * flopt.prod(x))
        return obj

    @staticmethod
    def create_variables(cat="Continuous", *args, **kwargs):
        x = flopt.Variable.array("x", 2, lowBound=-10, upBound=10, cat=cat)
        return x

    @staticmethod
    def minimum_obj(*args, **kwargs):
        return 0

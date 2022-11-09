import flopt


class Booth:
    @staticmethod
    def create_objective(*args, **kwargs):
        obj = lambda x: (x[0] + 2 * x[1] - 7) ** 2 + (2 * x[0] + x[1] - 5) ** 2
        return obj

    @staticmethod
    def create_variables(cat="Continuous", *args, **kwargs):
        x = flopt.Variable.array("x", 2, lowBound=-10, upBound=10, cat=cat)
        return x

    @staticmethod
    def minimum_obj(*args, **kwargs):
        return 0

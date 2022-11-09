import flopt


class Schaffer4:
    @staticmethod
    def create_objective(*args, **kwargs):
        obj = (
            lambda x: 0.5
            + (flopt.cos(flopt.sin(flopt.abs(x[0] ** 2 - x[1] ** 2))) ** 2 - 0.5)
            / (1 + 0.001 * flopt.sqnorm(x)) ** 2
        )
        return obj

    @staticmethod
    def create_variables(cat="Continuous", *args, **kwargs):
        x = flopt.Variable.array("x", 2, lowBound=-100, upBound=100, cat=cat)
        return x

    @staticmethod
    def minimum_obj(*args, **kwargs):
        return 0

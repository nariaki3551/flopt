import flopt


class Bukin:
    @staticmethod
    def create_objective(*args, **kwargs):
        obj = lambda x: 100 * (
            flopt.sqrt(flopt.abs(x[1] - 0.01 * x[0] * x[0]))
        ) + 0.01 * flopt.abs(x[0] + 10)
        return obj

    @staticmethod
    def create_variables(cat="Continuous", *args, **kwargs):
        x = flopt.variable_ndarray(
            [
                flopt.Variable(name=f"x1", lowBound=-15, upBound=-5, cat=cat),
                flopt.Variable(name=f"x2", lowBound=-3, upBound=3, cat=cat),
            ]
        )
        return x

    @staticmethod
    def minimum_obj(*args, **kwargs):
        return 0

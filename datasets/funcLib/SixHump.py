import flopt


class SixHump:
    @staticmethod
    def create_objective(*args, **kwargs):
        def obj(x):
            x1, x2 = x
            return (
                (4 - 2.1 * x1 * x1 + x1**4 / 3) * x1 * x1
                + x1 * x2
                + 4 * (x2 * x2 - 1) * x2 * x2
            )

        return obj

    @staticmethod
    def create_variables(cat="Continuous", *args, **kwargs):
        x = flopt.variable_ndarray(
            [
                flopt.Variable(name=f"x1", lowBound=-3, upBound=3, cat=cat),
                flopt.Variable(name=f"x2", lowBound=-2, upBound=2, cat=cat),
            ]
        )
        return x

    @staticmethod
    def minimum_obj(*args, **kwargs):
        return -1.0316

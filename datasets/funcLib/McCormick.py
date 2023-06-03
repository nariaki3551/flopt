import flopt


class McCormick:
    @staticmethod
    def create_objective(*args, **kwargs):
        obj = (
            lambda x: flopt.sin(x[0] + x[1])
            + (x[0] - x[1]) ** 2
            - 1.5 * x[0]
            + 2.5 * x[1]
            + 1
        )
        return obj

    @staticmethod
    def create_variables(cat="Continuous", *args, **kwargs):
        x = flopt.variable_ndarray(
            [
                flopt.Variable(name=f"x1", lowBound=-1.5, upBound=4, cat=cat),
                flopt.Variable(name=f"x2", lowBound=-3, upBound=4, cat=cat),
            ]
        )
        return x

    @staticmethod
    def minimum_obj(*args, **kwargs):
        return -1.9133

import flopt


class Shuberts:
    @staticmethod
    def create_objective(*args, **kwargs):
        def obj(x):
            x1, x2 = x
            m = 5
            c1 = flopt.sum(i * flopt.cos(i + (i + 1) * x1) for i in range(1, m + 1))
            c2 = flopt.sum(i * flopt.cos(i + (i + 1) * x2) for i in range(1, m + 1))
            return c1 * c2

        return obj

    @staticmethod
    def create_variables(cat="Continuous", *args, **kwargs):
        x = flopt.variable_ndarray(
            [
                flopt.Variable(name=f"x1", lowBound=-10, cat=cat),
                flopt.Variable(name=f"x2", upBound=10, cat=cat),
            ]
        )
        return x

    @staticmethod
    def minimum_obj(*args, **kwargs):
        return -186.7309

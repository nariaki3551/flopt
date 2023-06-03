import flopt


class Zahkarov:
    @staticmethod
    def create_objective(n):
        def obj(x):
            c1 = flopt.sum(x)
            c2 = flopt.sum(i * xi for i, xi in enumerate(x, 1))
            return c1 + (c2 / 2) ** 2 + (c2 / 2) ** 4

        return obj

    @staticmethod
    def create_variables(n, cat="Continuous"):
        x = flopt.Variable.array("x", n, cat=cat)
        return x

    @staticmethod
    def minimum_obj(n):
        return 0

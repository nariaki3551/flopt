import flopt


class Rosenbrock:
    @staticmethod
    def create_objective(n):
        obj = lambda x: flopt.sum(
            100 * (x[i + 1] - x[i] ** 2) ** 2 + (x[i] - 1) ** 2 for i in range(n - 1)
        )
        return obj

    @staticmethod
    def create_variables(n, cat="Continuous"):
        x = flopt.Variable.array("x", n, lowBound=-5, upBound=5, cat=cat)
        return x

    @staticmethod
    def minimum_obj(n):
        return 0

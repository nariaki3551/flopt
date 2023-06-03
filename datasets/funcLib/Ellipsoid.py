import flopt


class Ellipsoid:
    @staticmethod
    def create_objective(n):
        obj = lambda x: flopt.sum((1000 ** (i / n - 1) * x[i]) ** 2 for i in range(n))
        return obj

    @staticmethod
    def create_variables(n, cat="Continuous"):
        x = flopt.Variable.array("x", n, lowBound=-5.12, upBound=5.12, cat=cat)
        return x

    @staticmethod
    def minimum_obj(n):
        return 0

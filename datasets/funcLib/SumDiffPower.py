import flopt


class SumDiffPower:
    @staticmethod
    def create_objective(n):
        obj = lambda x: flopt.sum(flopt.abs(xi) ** (i + 1) for i, xi in enumerate(x, 1))
        return obj

    @staticmethod
    def create_variables(n, cat="Continuous"):
        x = flopt.Variable.array("x", n, lowBound=-1, upBound=1, cat=cat)
        return x

    @staticmethod
    def minimum_obj(n):
        return 0

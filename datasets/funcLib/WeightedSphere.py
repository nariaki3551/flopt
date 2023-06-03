import flopt


class WeightedSphere:
    @staticmethod
    def create_objective(n):
        obj = lambda x: flopt.sum(i * xi * xi for i, xi in enumerate(x, 1))
        return obj

    @staticmethod
    def create_variables(n, cat="Continuous"):
        x = flopt.Variable.array("x", n, lowBound=-5.12, upBound=5.12, cat=cat)
        return x

    @staticmethod
    def minimum_obj(n):
        return 0

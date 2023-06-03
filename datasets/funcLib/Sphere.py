import flopt


class Sphere:
    @staticmethod
    def create_objective(n):
        obj = lambda x: flopt.sqnorm(x)
        return obj

    @staticmethod
    def create_variables(n, cat="Continuous"):
        x = flopt.Variable.array("x", n, cat=cat)
        return x

    @staticmethod
    def minimum_obj(n):
        return 0

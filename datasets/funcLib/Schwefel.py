import flopt


class Schwefel:
    @staticmethod
    def create_objective(n):
        obj = lambda x: -flopt.sum(x * flopt.sin(flopt.sqrt(flopt.abs(x))))
        return obj

    @staticmethod
    def create_variables(n, cat="Continuous"):
        x = flopt.Variable.array("x", n, lowBound=-500, upBound=500, cat=cat)
        return x

    @staticmethod
    def minimum_obj(n):
        return -418.9829 * n

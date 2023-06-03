import flopt


class Griewank:
    @staticmethod
    def create_objective(n):
        obj = (
            lambda x: 1
            + flopt.sqnorm(x) / 4000
            - (flopt.prod(flopt.cos(xi / i**0.5) for i, xi in enumerate(x, 1)))
        )
        return obj

    @staticmethod
    def create_variables(n, cat="Continuous"):
        x = flopt.Variable.array("x", n, lowBound=-600, upBound=600, cat=cat)
        return x

    @staticmethod
    def minimum_obj(n):
        return 0

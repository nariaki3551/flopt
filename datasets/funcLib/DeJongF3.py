import flopt


class DeJongF3:
    @staticmethod
    def create_objective(*args, **kwargs):
        obj = lambda x: flopt.sum(flopt.floor(x))
        return obj

    @staticmethod
    def create_variables(cat="Continuous", *args, **kwargs):
        x = flopt.Variable.array("x", 5, lowBound=-5.12, upBound=5.12, cat=cat)
        return x

    @staticmethod
    def minimum_obj(n):
        return -6 * n

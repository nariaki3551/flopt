import flopt


class Eggholder:
    @staticmethod
    def create_objective(*args, **kwargs):
        def obj(x):
            x1, x2 = x
            return -(x2 + 47) * flopt.sin(
                flopt.sqrt(flopt.abs(x2 + x1 / 2 + 47))
            ) - x1 * flopt.sin(flopt.sqrt(flopt.abs(x1 - x2 - 47)))

        return obj

    @staticmethod
    def create_variables(cat="Continuous", *args, **kwargs):
        x = flopt.Variable.array("x", 2, lowBound=-512, upBound=512, cat=cat)
        return x

    @staticmethod
    def minimum_obj(*args, **kwargs):
        return -959.6407

import flopt


def create_objective(*args, **kwargs):
    def obj(x):
        x1, x2 = x
        return 2 * x1 * x1 - 1.05 * x1**4 + x1**6 / 6 + x1 * x2 + x2 * x2

    return obj


def create_variables(*args, **kwargs):
    variables = flopt.Variable.array("x", 2, lowBound=-5, upBound=5, cat="Continuous")
    return variables


def minimum_obj(*args, **kwargs):
    return 0

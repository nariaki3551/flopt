import flopt


def create_objective(*args, **kwargs):
    def obj(x):
        x1, x2 = x
        return (x1 + 2 * x2 - 7) ** 2 + (2 * x1 + x2 - 5) ** 2

    return obj


def create_variables(*args, **kwargs):
    variables = flopt.Variable.array("x", 2, lowBound=-10, upBound=10, cat="Continuous")
    return variables


def minimum_obj(*args, **kwargs):
    return 0

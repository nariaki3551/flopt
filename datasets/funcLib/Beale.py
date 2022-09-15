import flopt


def create_objective(*args, **kwargs):
    def obj(x):
        x1, x2 = x
        return (
            (1.5 - x1 + x1 * x2) ** 2
            + (2.25 - x1 + x1 * x2 * x2) ** 2
            + (2.625 - x1 + x1 * x2 * x2 * x2) ** 2
        )

    return obj


def create_variables(cat="Continuous", *args, **kwargs):
    variables = flopt.Variable.array("x", 2, lowBound=-4.5, upBound=4.5, cat=cat)
    return variables


def minimum_obj(*args, **kwargs):
    return 0

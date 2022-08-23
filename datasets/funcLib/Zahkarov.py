import flopt


def create_objective(n):
    def obj(x):
        c1 = flopt.Sum(x)
        c2 = flopt.Sum(i * xi for i, xi in enumerate(x, 1))
        return c1 + (c2 / 2) ** 2 + (c2 / 2) ** 4

    return obj


def create_variables(n):
    variables = flopt.Variable.array("x", n, cat="Continuous")
    return variables


def minimum_obj(n):
    return 0

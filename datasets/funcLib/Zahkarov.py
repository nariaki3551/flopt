import flopt


def create_objective(n):
    def obj(x):
        c1 = sum(x)
        c2 = sum(i * xi for i, xi in enumerate(x, 1))
        return c1 + (c2 / 2) ** 2 + (c2 / 2) ** 4

    return obj


def create_variables(n, cat="Continuous"):
    variables = flopt.Variable.array("x", n, cat=cat)
    return variables


def minimum_obj(n):
    return 0

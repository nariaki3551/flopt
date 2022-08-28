import flopt


def create_objective(n):
    def obj(x):
        return flopt.Sum(xi * xi for xi in x)

    return obj


def create_variables(n):
    variables = flopt.Variable.array("x", n, cat="Continuous")
    return variables


def minimum_obj(n):
    return 0

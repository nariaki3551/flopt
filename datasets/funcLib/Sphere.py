import flopt


def create_objective(n):
    def obj(x):
        return flopt.Sqnorm(x)

    return obj


def create_variables(n, cat="Continuous"):
    variables = flopt.Variable.array("x", n, cat=cat)
    return variables


def minimum_obj(n):
    return 0

import flopt


def create_objective(n):
    def obj(x):
        return sum(abs(xi) ** (i + 1) for i, xi in enumerate(x, 1))

    return obj


def create_variables(n, cat="Continuous"):
    variables = flopt.Variable.array("x", n, lowBound=-1, upBound=1, cat=cat)
    return variables


def minimum_obj(n):
    return 0

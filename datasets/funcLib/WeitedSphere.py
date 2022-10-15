import flopt


def create_objective(n):
    def obj(x):
        return sum(i * xi * xi for i, xi in enumerate(x, 1))

    return obj


def create_variables(n, cat="Continuous"):
    variables = flopt.Variable.array("x", n, lowBound=-5.12, upBound=5.12, cat=cat)
    return variables


def minimum_obj(n):
    return 0

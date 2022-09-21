import flopt


def create_objective(n):
    def obj(x):
        n = len(x)

        def obj_i(i):
            return 100 * (x[i + 1] - x[i] ** 2) ** 2 + (x[i] - 1) ** 2

        return sum(obj_i(i) for i in range(n - 1))

    return obj


def create_variables(n, cat="Continuous"):
    variables = flopt.Variable.array("x", n, lowBound=-5, upBound=5, cat=cat)
    return variables


def minimum_obj(n):
    return 0

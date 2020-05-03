from flopt import Variable

def create_objective(n):
    def obj(x):
        return sum(i*xi*xi for i, xi in enumerate(x, 1))
    return obj

def create_variables(n):
    variables = [
        Variable(
            name=f'x{i}',
            lowBound=-5.12,
            upBound=5.12,
            cat='Continuous'
        )
        for i in range(n)
    ]
    return variables


def minimum_obj(n):
    return 0

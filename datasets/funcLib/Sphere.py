from flopt import Variable

def create_objective(n):
    def obj(x):
        return sum(xi*xi for xi in x)
    return obj

def create_variables(n):
    variables = [
        Variable(
            name=f'x{i}',
            cat='Continuous'
        )
        for i in range(n)
    ]
    return variables


def minimum_obj(n):
    return 0

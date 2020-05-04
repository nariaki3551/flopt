from flopt import Variable

def create_objective(*args, **kwargs):
    def obj(x):
        x1, x2 = x
        return (4-2.1*x1*x1+x1**4/3)*x1*x1+x1*x2+4*(x2*x2-1)*x2*x2
    return obj

def create_variables(*args, **kwargs):
    variables = [
        Variable(
            name=f'x1',
            lowBound=-3,
            upBound=3,
            cat='Continuous'
        ),
        Variable(
            name=f'x2',
            lowBound=-2,
            upBound=2,
            cat='Continuous'
        )
    ]
    return variables

def minimum_obj(*args, **kwargs):
    return -1.0316

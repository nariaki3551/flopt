from flopt import Variable

def create_objective(*args, **kwargs):
    def obj(x):
        x1, x2 = x
        c1 = (1+0.05*(x1*x1+(x2-10)*(x2-10)))
        c2 = (1+0.05*((x1-10)*(x1-10)+x2*x2))
        c3 = (1*0.03*((x1+10)*(x1+10)+x2*x2))
        c4 = (1+0.05*((x1-5)*(x1-5)+(x2+10)*(x2+10)))
        c5 = (1+0.1*((x1+5)*(x1+5)+(x2+10)*(x2+10)))
        c6 = 1+0.0001*(x1*x1+x2*x2)**(1.2)
        return (1 - 1/c1 - 1/c2 - 1/c3 - 1/c4 - 1/c5)*c6
    return obj

def create_variables(*args, **kwargs):
    variables = [
        Variable(
            name=f'x{i}',
            lowBound=-20,
            upBound=20,
            cat='Continuous'
        )
        for i in [0, 1]
    ]
    return variables

def minimum_obj(*args, **kwargs):
    return -1.4616

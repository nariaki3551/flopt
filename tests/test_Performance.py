import flopt
from flopt import Variable, Problem, Solver
from flopt.performance import CustomDataset

a = Variable('a', lowBound=2, upBound=4, cat='Continuous')
b = Variable('b', lowBound=2, upBound=4, cat='Continuous')

prob = Problem()
prob += a + b

def test_compute_nosolver():
    logs = flopt.performance.compute(prob, timelimit=1, msg=True)    

def test_compute_RandomSearch():
    rs_solver = Solver('RandomSearch')
    logs = flopt.performance.compute(
        prob, rs_solver,
        timelimit=0.1, msg=True
    )

def test_CustomDataset():
    cd = CustomDataset(name='user')
    cd += prob  # add problem

    log = flopt.performance.compute(
        cd, timelimit=0.1, msg=True
    )

def test_compute_permutation():
    prob.prob_type = 'permutation'
    logs = flopt.performance.compute(prob, timelimit=0.1, msg=True)

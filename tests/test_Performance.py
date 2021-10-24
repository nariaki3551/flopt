import pytest

import flopt
from flopt import Variable, Problem, Solver
from flopt.performance import CustomDataset

@pytest.fixture(scope='function')
def a():
    return Variable('a', lowBound=2, upBound=4, cat='Continuous')

@pytest.fixture(scope='function')
def b():
    return Variable('b', lowBound=2, upBound=4, cat='Continuous')

@pytest.fixture(scope='function')
def prob(a, b):
    _prob = Problem()
    _prob += a + b
    return _prob

def test_compute_nosolver(prob):
    logs = flopt.performance.compute(prob, timelimit=0.5, msg=True)

def test_compute_RandomSearch(prob):
    rs_solver = Solver('RandomSearch')
    logs = flopt.performance.compute(
        prob, rs_solver,
        timelimit=0.1, msg=True
    )

def test_CustomDataset(prob):
    cd = CustomDataset(name='user')
    cd += prob  # add problem

    log = flopt.performance.compute(
        cd, timelimit=0.1, msg=True
    )

def test_compute_permutation(prob):
    prob.prob_type = 'permutation'
    logs = flopt.performance.compute(prob, timelimit=0.1, msg=True)

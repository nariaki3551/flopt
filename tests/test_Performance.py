import pytest

import flopt
from flopt import Variable, Problem, Solver
from flopt.performance import CustomDataset


@pytest.fixture(scope="function")
def a():
    return Variable("a", lowBound=2, upBound=4, cat="Continuous")


@pytest.fixture(scope="function")
def b():
    return Variable("b", lowBound=2, upBound=4, cat="Continuous")


@pytest.fixture(scope="function")
def prob(a, b):
    _prob = Problem("test")
    _prob += a + b
    return _prob


def test_tsp_dataset():
    dataset = flopt.performance.get_dataset("tsp")
    instance = dataset["test8"]

    # lp
    milp = Solver("ScipyMilpSearch")
    solvable, prob = instance.createProblem(milp)
    assert solvable
    prob.solve(milp, msg=True)
    obj_value = prob.getObjectiveValue()

    # 2-opt
    two_opt = Solver("2-Opt")
    solvable, prob = instance.createProblem(two_opt)
    prob.setBestBound(obj_value)
    assert solvable
    prob.solve(two_opt, timelimit=0.5, msg=True)


def test_func_dataset():
    dataset = flopt.performance.get_dataset("func")
    instance = dataset["Ackley"]

    scipy_search = Solver("ScipySearch")
    solvable, prob = instance.createProblem(scipy_search)
    assert solvable
    prob.solve(scipy_search, msg=True)


def test_mip_dataset():
    dataset = flopt.performance.get_dataset("mip")
    instance = dataset["markshare2"]
    scipy_search = Solver("ScipyMilpSearch")
    solvable, prob = instance.createProblem(scipy_search)
    assert solvable
    prob.solve(scipy_search, msg=True)


def test_Dataset_list():
    flopt.performance.Dataset_list()


def test_compute_nosolver(prob):
    logs = flopt.performance.compute(prob, timelimit=0.5, msg=True)


def test_compute_RandomSearch(prob):
    rs_solver = Solver("RandomSearch")
    logs = flopt.performance.compute(prob, rs_solver, timelimit=0.1, msg=True)


def test_CustomDataset(prob):
    cd = CustomDataset(name="user")
    cd += prob  # add problem

    log = flopt.performance.compute(cd, timelimit=0.1, msg=True)


def test_compute_permutation(prob):
    prob.prob_type = "permutation"
    logs = flopt.performance.compute(prob, timelimit=0.1, msg=True)

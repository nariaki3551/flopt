import pytest

import flopt
from flopt import Variable, Problem, Solver, Solver_list, CustomExpression

@pytest.fixture(scope='function')
def variables():
    vals = [
        Variable('a', 0, 1, 'Integer'),
        Variable('b', 1, 2, 'Continuous'),
        Variable('c', 1, 3, 'Continuous'),
    ]
    return vals

@pytest.fixture(scope='function')
def prob(variables):
    a, b, c = variables
    _prob = Problem(name='Test')
    _prob += a + b + c
    return _prob

@pytest.fixture(scope='function')
def prob_with_const(variables):
    # Problem with constraint
    a, b, c = variables
    _prob = Problem(name='TestC')
    _prob += a + b + c
    _prob += a + b >= 2
    return _prob

@pytest.fixture(scope='function')
def prob_nonlinear(variables):
    # Non-Linear problem
    a, b, c = variables
    _prob = Problem('Non-Linear')
    _prob += a*b*c
    _prob += a + b >= 2
    return _prob

@pytest.fixture(scope='function')
def prob_perm(variables):
    # Permutation Problem
    a, b, c = variables
    p = Variable('p', 0, 4, 'Permutation')
    _prob = Problem('TestP')
    def obj(p):
        return p[-1] - p[0]
    _prob +=  CustomExpression(obj, [p])
    return _prob

@pytest.fixture(scope='function')
def callback():
    def _callback(solutions, best_solution, best_obj_value):
        pass
    return _callback

def test_Solver_list():
    Solver_list()

def test_RandomSearch(prob, callback):
    solver = Solver(algo='RandomSearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob.solve(solver, timelimit=1)

def test_RandomSearch2(prob_perm, callback):
    solver = Solver(algo='RandomSearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob_perm.solve(solver, timelimit=1)

def test_RandomSearch_available(prob, prob_with_const, prob_nonlinear, prob_perm):
    solver = Solver(algo='RandomSearch')
    assert solver.available(prob) == True
    assert solver.available(prob_with_const) == False
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_perm) == True


def test_2Opt(prob_perm, callback):
    solver = Solver(algo='2-Opt')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob_perm.solve(solver, timelimit=1)

def test_2Opt_available(prob, prob_with_const, prob_nonlinear, prob_perm):
    solver = Solver(algo='2-Opt')
    assert solver.available(prob) == False
    assert solver.available(prob_with_const) == False
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_perm) == True


def test_OptunaTPESearch(prob, callback):
    solver = Solver(algo='OptunaTPESearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob.solve(solver, timelimit=1)

def test_OptunaTPESearch_available(prob, prob_with_const, prob_nonlinear, prob_perm):
    solver = Solver(algo='OptunaTPESearch')
    assert solver.available(prob) == True
    assert solver.available(prob_with_const) == False
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_perm) == False


def test_OptunaCmaEsSearch(prob, callback):
    solver = Solver(algo='OptunaCmaEsSearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob.solve(solver, timelimit=1)

def test_OptunaCmaEsSearch_available(prob, prob_with_const, prob_nonlinear, prob_perm):
    solver = Solver(algo='OptunaCmaEsSearch')
    assert solver.available(prob) == True
    assert solver.available(prob_with_const) == False
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_perm) == False


def test_HyperoptTPESearch(prob, callback):
    solver = Solver(algo='HyperoptTPESearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob.solve(solver, timelimit=1)

def test_HyperoptTPESearch_available(prob, prob_with_const, prob_nonlinear, prob_perm):
    solver = Solver(algo='HyperoptTPESearch')
    assert solver.available(prob) == True
    assert solver.available(prob_with_const) == False
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_perm) == False


def test_SFLA(prob, callback):
    solver = Solver(algo="SFLA")
    solver.setParams(
        n_memeplex=5, n_frog_per_memeplex=10, n_memetic_iter=100,
        n_iter=1000, max_step=0.01, msg=True, callbacks=[callback],
    )
    prob.solve(solver=solver, timelimit=10)

def test_SFLA_available(prob, prob_with_const, prob_nonlinear, prob_perm):
    solver = Solver(algo='SFLA')
    assert solver.available(prob) == True
    assert solver.available(prob_with_const) == False
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_perm) == False


def test_PulpSearch1(prob, callback):
    solver = Solver(algo='PulpSearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob.solve(solver, timelimit=1)

def test_PulpSearch2(prob_with_const, callback):
    solver = Solver(algo='PulpSearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob_with_const.solve(solver, timelimit=1)

def test_PulpSearch_available(prob, prob_with_const, prob_nonlinear, prob_perm):
    solver = Solver(algo='PulpSearch')
    assert solver.available(prob) == True
    assert solver.available(prob_with_const) == True
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_perm) == False

def test_PulpSearch_available_Error(prob_nonlinear, callback):
    solver = Solver(algo='PulpSearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    try:
        prob_nonlinear.solve(solver, timelimit=1)
        assert False
    except flopt.constants.SolverError:
        assert True


def test_ScipySearch1(prob, callback):
    solver = Solver(algo='ScipySearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob.solve(solver, timelimit=1)

def test_ScipySearch2(prob_with_const, callback):
    solver = Solver(algo='ScipySearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob_with_const.solve(solver, timelimit=1)

def test_ScipySearch_available(prob, prob_with_const, prob_nonlinear, prob_perm):
    solver = Solver(algo='ScipySearch')
    assert solver.available(prob) == True
    assert solver.available(prob_with_const) == True
    assert solver.available(prob_nonlinear) == True
    assert solver.available(prob_perm) == False

def test_AutoSearch1(prob, callback):
    solver = Solver(algo='auto')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob.solve(solver, timelimit=1)

def test_AutoSearch2(prob_with_const, callback):
    solver = Solver(algo='auto')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob_with_const.solve(solver, timelimit=1)

def test_AutoSearch3(prob_nonlinear, callback):
    solver = Solver(algo='auto')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob_nonlinear.solve(solver, timelimit=1)

def test_AutoSearch4(prob_with_const, callback):
    solver = Solver(algo='auto')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob_with_const.solve(solver, timelimit=1)

def test_AutoSearch_available(prob, prob_with_const, prob_nonlinear, prob_perm):
    solver = Solver(algo='auto')
    assert solver.available(prob) == True
    assert solver.available(prob_with_const) == True
    assert solver.available(prob_nonlinear) == True
    assert solver.available(prob_perm) == True



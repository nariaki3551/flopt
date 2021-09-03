import pytest

import flopt
import flopt.error
from flopt import Variable, Problem, Solver, Solver_list, CustomExpression


@pytest.fixture(scope='function')
def prob():
    a = Variable('a', 0, 1, 'Integer')
    _prob = Problem(name='Test')
    _prob += a
    return _prob

@pytest.fixture(scope='function')
def prob_no_obj():
    a = Variable('a', 0, 1, 'Integer')
    _prob = Problem(name='Test')
    _prob += a <= 0
    return _prob

@pytest.fixture(scope='function')
def prob_only_continuous():
    b = Variable('b', 1, 2, 'Continuous')
    c = Variable('c', 1, 3, 'Continuous')
    _prob = Problem(name='Test')
    _prob += b + c
    return _prob

@pytest.fixture(scope='function')
def prob_with_const():
    # Problem with constraint
    a = Variable('a', 0, 1, 'Integer')
    b = Variable('b', 1, 2, 'Continuous')
    c = Variable('c', 1, 3, 'Continuous')
    _prob = Problem(name='TestC')
    _prob += a + b + c
    _prob += a + b >= 2
    return _prob

@pytest.fixture(scope='function')
def prob_qp():
    # Problem with constraint
    a = Variable('a', 0, 1, 'Integer')
    b = Variable('b', 1, 2, 'Continuous')
    c = Variable('c', 1, 3, 'Continuous')
    _prob = Problem(name='TestC')
    _prob += 2*b*b + b*c + b + c
    _prob += b + c == 1
    return _prob

@pytest.fixture(scope='function')
def prob_nonlinear():
    # Non-Linear problem
    a = Variable('a', 0, 1, 'Integer')
    b = Variable('b', 1, 2, 'Continuous')
    c = Variable('c', 1, 3, 'Continuous')
    _prob = Problem('Non-Linear')
    _prob += a*b*c
    _prob += a + b >= 2
    return _prob

@pytest.fixture(scope='function')
def prob_ising():
    a = Variable('a', cat='Spin')
    b = Variable('b', cat='Spin')
    _prob = Problem('ising')
    _prob += 1 - a * b - a
    return _prob

@pytest.fixture(scope='function')
def prob_ising_const():
    a = Variable('a', cat='Spin')
    b = Variable('b', cat='Spin')
    _prob = Problem('ising')
    _prob += 1 - a * b - a
    _prob += a * b == 1
    _prob += a + b <= 0
    return _prob

@pytest.fixture(scope='function')
def prob_perm():
    # Permutation Problem
    _prob = Problem('TestP')
    p = Variable('p', 0, 4, 'Permutation')
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
    prob.solve(solver, timelimit=0.5)

def test_RandomSearch2(prob_perm, callback):
    solver = Solver(algo='RandomSearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob_perm.solve(solver, timelimit=0.5)

def test_RandomSearch_available(prob, prob_with_const, prob_qp, prob_nonlinear, prob_perm):
    solver = Solver(algo='RandomSearch')
    assert solver.available(prob) == True
    assert solver.available(prob_with_const) == False
    assert solver.available(prob_qp) == False
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_perm) == True


def test_2Opt(prob_perm, callback):
    solver = Solver(algo='2-Opt')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob_perm.solve(solver, timelimit=0.5)

def test_2Opt_available(prob, prob_with_const, prob_qp, prob_nonlinear, prob_perm):
    solver = Solver(algo='2-Opt')
    assert solver.available(prob) == False
    assert solver.available(prob_with_const) == False
    assert solver.available(prob_qp) == False
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_perm) == True


def test_OptunaTPESearch(prob, callback):
    solver = Solver(algo='OptunaTPESearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob.solve(solver, timelimit=0.5)

def test_OptunaTPESearch_available(prob, prob_with_const, prob_qp, prob_nonlinear, prob_perm):
    solver = Solver(algo='OptunaTPESearch')
    assert solver.available(prob) == True
    assert solver.available(prob_with_const) == False
    assert solver.available(prob_qp) == False
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_perm) == False


def test_OptunaCmaEsSearch(prob, callback):
    solver = Solver(algo='OptunaCmaEsSearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob.solve(solver, timelimit=0.5)

def test_OptunaCmaEsSearch_available(prob, prob_with_const, prob_qp, prob_nonlinear, prob_perm):
    solver = Solver(algo='OptunaCmaEsSearch')
    assert solver.available(prob) == True
    assert solver.available(prob_with_const) == False
    assert solver.available(prob_qp) == False
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_perm) == False


def test_HyperoptTPESearch(prob, callback):
    solver = Solver(algo='HyperoptTPESearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob.solve(solver, timelimit=0.5)

def test_HyperoptTPESearch_available(prob, prob_with_const, prob_qp, prob_nonlinear, prob_perm):
    solver = Solver(algo='HyperoptTPESearch')
    assert solver.available(prob) == True
    assert solver.available(prob_with_const) == False
    assert solver.available(prob_qp) == False
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_perm) == False


def test_SFLA(prob, callback):
    solver = Solver(algo="SFLA")
    solver.setParams(
        n_memeplex=5, n_frog_per_memeplex=10, n_memetic_iter=100,
        n_iter=1000, max_step=0.01, msg=True, callbacks=[callback],
    )
    prob.solve(solver=solver, timelimit=2, msg=True)

def test_SFLA_available(prob, prob_with_const, prob_qp, prob_nonlinear, prob_perm):
    solver = Solver(algo='SFLA')
    assert solver.available(prob) == True
    assert solver.available(prob_with_const) == False
    assert solver.available(prob_qp) == False
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_perm) == False


def test_PulpSearch1(prob, callback):
    solver = Solver(algo='PulpSearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob.solve(solver, timelimit=0.5)

def test_PulpSearch2(prob_with_const, callback):
    solver = Solver(algo='PulpSearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob_with_const.solve(solver, timelimit=0.5)

def test_PulpSearch2(prob_no_obj, callback):
    solver = Solver(algo='PulpSearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob_no_obj.solve(solver, timelimit=0.5)

def test_PulpSearch_available(prob, prob_with_const, prob_qp, prob_nonlinear, prob_perm):
    solver = Solver(algo='PulpSearch')
    assert solver.available(prob) == True
    assert solver.available(prob_with_const) == True
    assert solver.available(prob_qp) == False
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_perm) == False

def test_PulpSearch_available_Error(prob_nonlinear, callback):
    solver = Solver(algo='PulpSearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    try:
        prob_nonlinear.solve(solver, timelimit=0.5)
        assert False
    except flopt.error.SolverError:
        assert True


def test_ScipySearch1(prob_only_continuous, callback):
    solver = Solver(algo='ScipySearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob_only_continuous.solve(solver, timelimit=0.5)

def test_ScipySearch_available(prob, prob_only_continuous, prob_with_const, prob_qp, prob_nonlinear, prob_perm):
    solver = Solver(algo='ScipySearch')
    assert solver.available(prob) == False
    assert solver.available(prob_only_continuous) == True
    assert solver.available(prob_with_const) == False
    assert solver.available(prob_qp) == True
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_perm) == False


def test_ScipyLpSearch1(prob_only_continuous, callback):
    solver = Solver(algo='ScipyLpSearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob_only_continuous.solve(solver, timelimit=0.5)

def test_ScipyLpSearch_available(prob, prob_only_continuous, prob_with_const, prob_qp, prob_nonlinear, prob_perm):
    solver = Solver(algo='ScipyLpSearch')
    assert solver.available(prob) == False
    assert solver.available(prob_only_continuous) == True
    assert solver.available(prob_with_const) == False
    assert solver.available(prob_qp) == False
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_perm) == False



def test_CvxoptQpSearch1(prob_only_continuous, callback):
    solver = Solver(algo='CvxoptQpSearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob_only_continuous.solve(solver, timelimit=0.5)

def test_CvxoptQpSearch2(prob_qp, callback):
    solver = Solver(algo='CvxoptQpSearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob_qp.solve(solver, timelimit=0.5)


def test_AmplifySearch_available(
        prob, prob_only_continuous, prob_with_const,
        prob_qp, prob_nonlinear,
        prob_ising, prob_ising_const,
        prob_perm,
        ):
    solver = Solver(algo='AmplifySearch')
    assert solver.available(prob) == False
    assert solver.available(prob_only_continuous) == False
    assert solver.available(prob_with_const) == False
    assert solver.available(prob_qp) == False
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_ising) == True
    assert solver.available(prob_ising_const) == True
    assert solver.available(prob_perm) == False

def test_AmplifySearch1(prob_ising, callback, request):
    token = request.config.getoption('amplify_token')
    if token is None:
        return True
    solver = Solver(algo='AmplifySearch')
    solver.setParams(token=token)
    prob_ising.solve(solver, timelimit=1, msg=True)

def test_AmplifySearch2(prob_ising_const, callback, request):
    token = request.config.getoption('amplify_token')
    if token is None:
        return True
    solver = Solver(algo='AmplifySearch')
    solver.setParams(token=token)
    prob_ising_const.solve(solver, timelimit=1, msg=True)


def test_CvxoptQpSearch1(prob_only_continuous, callback):
    solver = Solver(algo='CvxoptQpSearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob_only_continuous.solve(solver, timelimit=0.5)

def test_CvxoptQpSearch2(prob_qp, callback):
    solver = Solver(algo='CvxoptQpSearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob_qp.solve(solver, timelimit=0.5)


def test_ScipyLpSearch_available(prob, prob_only_continuous, prob_with_const, prob_qp, prob_nonlinear, prob_perm):
    solver = Solver(algo='ScipyLpSearch')
    assert solver.available(prob) == False
    assert solver.available(prob_only_continuous) == True
    assert solver.available(prob_with_const) == False
    assert solver.available(prob_qp) == False
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_perm) == False


def test_AutoSearch1(prob, callback):
    solver = Solver(algo='auto')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob.solve(solver, timelimit=0.5)

def test_AutoSearch2(prob_with_const, callback):
    solver = Solver(algo='auto')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob_with_const.solve(solver, timelimit=0.5)

# def test_AutoSearch3(prob_nonlinear, callback):
#     solver = Solver(algo='auto')
#     solver.setParams(n_trial=10, callbacks=[callback])
#     prob_nonlinear.solve(solver, timelimit=0.5)

def test_AutoSearch4(prob_with_const, callback):
    solver = Solver(algo='auto')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob_with_const.solve(solver, timelimit=0.5)

def test_AutoSearch_available(prob, prob_with_const, prob_qp, prob_nonlinear, prob_perm):
    solver = Solver(algo='auto')
    assert solver.available(prob) == True
    assert solver.available(prob_with_const) == True
    assert solver.available(prob_qp) == True
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_perm) == True



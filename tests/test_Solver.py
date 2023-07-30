import pytest

import flopt
import flopt.error
from flopt import (
    Variable,
    Problem,
    Solver,
    Solver_list,
    CustomExpression,
    estimate_problem_type,
)


@pytest.fixture(scope="function")
def prob():
    a = Variable("a", 0, 1, "Integer")
    _prob = Problem(name="Test")
    _prob += a
    return _prob


@pytest.fixture(scope="function")
def prob_no_obj():
    a = Variable("a", 0, 1, "Integer")
    _prob = Problem(name="Test")
    _prob += a <= 0
    return _prob


@pytest.fixture(scope="function")
def prob_only_continuous():
    b = Variable("b", 1, 2, "Continuous")
    c = Variable("c", 1, 3, "Continuous")
    _prob = Problem(name="Test")
    _prob += b + c
    return _prob


@pytest.fixture(scope="function")
def prob_with_const():
    # Problem with constraint
    a = Variable("a", 0, 1, "Integer")
    b = Variable("b", 1, 2, "Continuous")
    c = Variable("c", 1, 3, "Continuous")
    _prob = Problem(name="TestC")
    _prob += a + b + c
    _prob += a + b >= 2
    return _prob


@pytest.fixture(scope="function")
def prob_lp():
    a = flopt.Variable("a", cat="Continuous", ini_value=0)
    b = flopt.Variable("b", cat="Continuous", ini_value=0)
    _prob = flopt.Problem("TestLp", sense="Maximize")
    _prob += 1 * a + 3 * b <= 30
    _prob += 2 * a + 1 * b <= 40
    _prob += a >= 0
    _prob += b >= 0
    _prob += a + 2 * b
    return _prob


@pytest.fixture(scope="function")
def prob_qp():
    # Problem with constraint
    a = Variable("a", 0, 1, "Integer")
    b = Variable("b", 1, 2, "Continuous", ini_value=1)
    c = Variable("c", 0, 3, "Continuous")
    _prob = Problem(name="TestC")
    _prob += 2 * b * b + b * c + b + c
    _prob += b + c == 1
    return _prob


@pytest.fixture(scope="function")
def prob_nonlinear():
    # Non-Linear problem
    a = Variable("a", 0, 1, "Integer")
    b = Variable("b", 1, 2, "Continuous")
    c = Variable("c", 1, 3, "Continuous")
    _prob = Problem("Non-Linear")
    _prob += a * b * c
    _prob += a + b >= 2
    return _prob


@pytest.fixture(scope="function")
def prob_ising():
    a = Variable("a", cat="Spin")
    b = Variable("b", cat="Spin")
    _prob = Problem("ising")
    _prob += 1 - a * b - a
    return _prob


@pytest.fixture(scope="function")
def prob_ising_const():
    a = Variable("a", cat="Spin")
    b = Variable("b", cat="Spin")
    _prob = Problem("ising")
    _prob += 1 - a * b - a
    _prob += a * b == 1
    _prob += a + b <= 0
    return _prob


@pytest.fixture(scope="function")
def prob_perm():
    # Permutation Problem
    _prob = Problem("TestP")
    p = Variable("p", 0, 4, "Permutation")

    def obj(p):
        return p[-1] - p[0]

    _prob += CustomExpression(obj, [p])
    return _prob


@pytest.fixture(scope="function")
def callback():
    def _callback(solutions, best_solution, best_obj_value):
        pass

    return _callback


def test_Solver_list():
    Solver_list()


def test_RandomSearch(prob, callback):
    """test to solve problem has only objective"""
    prob.solve(solver="Random", n_trial=10, timelimit=0.5, callbacks=[callback])


def test_RandomSearch2(prob_perm, callback):
    """test to solve problem has permutation variable"""
    prob_perm.solve(solver="Random", n_trial=10, timelimit=0.5, callbacks=[callback])


def test_RandomSearch3(prob_only_continuous, callback):
    """test to solve problem with optimized_variables"""
    variables = list(prob_only_continuous.getVariables())
    non_optimized_values = [var.value() for var in variables[1:]]
    prob_only_continuous.solve(
        solver="Random",
        n_trial=10,
        timelimit=0.5,
        callbacks=[callback],
        optimized_variables=variables[:1],
    )
    assert all(
        var.value() == value for var, value in zip(variables[1:], non_optimized_values)
    )


def test_RandomSearch_available(
    prob, prob_with_const, prob_qp, prob_nonlinear, prob_perm
):
    solver = Solver(algo="Random")
    assert solver.available(prob) == True
    assert solver.available(prob_with_const) == False
    assert solver.available(prob_qp) == False
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_perm) == True


def test_2Opt(prob_perm, callback):
    prob_perm.solve(solver="2-Opt", n_trial=10, timelimit=0.5, callbacks=[callback])


def test_2Opt_available(prob, prob_with_const, prob_qp, prob_nonlinear, prob_perm):
    solver = Solver(algo="2-Opt")
    assert solver.available(prob) == False
    assert solver.available(prob_with_const) == False
    assert solver.available(prob_qp) == False
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_perm) == True


def test_OptunaTPESearch1(prob, callback):
    """test to solve problem has only objective"""
    prob.solve(solver="OptunaTPE", n_trial=10, timelimit=0.5, callbacks=[callback])


def test_OptunaTPESearch2(prob_only_continuous, callback):
    """test to solve problem with optimized_variables"""
    variables = list(prob_only_continuous.getVariables())
    non_optimized_values = [var.value() for var in variables[1:]]
    prob_only_continuous.solve(
        solver="OptunaTPE",
        n_trial=10,
        timelimit=0.5,
        callbacks=[callback],
        optimized_variables=variables[:1],
    )
    assert all(
        var.value() == value for var, value in zip(variables[1:], non_optimized_values)
    )


def test_OptunaTPESearch3(prob_qp, callback):
    prob_qp.solve(solver="OptunaTPE", n_trial=10, timelimit=0.5, callbacks=[callback])


def test_OptunaTPESearch4(prob_nonlinear, callback):
    prob_nonlinear.solve(
        solver="OptunaTPE", n_trial=10, timelimit=0.5, callbacks=[callback]
    )


def test_OptunaTPESearch_available(
    prob, prob_only_continuous, prob_with_const, prob_qp, prob_nonlinear, prob_perm
):
    solver = Solver(algo="OptunaTPE")
    assert solver.available(prob) == True
    assert solver.available(prob_only_continuous) == True
    assert solver.available(prob_with_const) == True
    assert solver.available(prob_qp) == True
    assert solver.available(prob_nonlinear) == True
    assert solver.available(prob_perm) == False


def test_OptunaCmaEsSearch1(prob, callback):
    """test to solve problem has only objective"""
    prob.solve(solver="OptunaCmaEs", n_trial=10, timelimit=0.5, callbacks=[callback])


def test_OptunaCmaEsSearch2(prob_only_continuous, callback):
    """test to solve problem with optimized_variables"""
    variables = list(prob_only_continuous.getVariables())
    non_optimized_values = [var.value() for var in variables[1:]]
    prob_only_continuous.solve(
        solver="OptunaCmaEs",
        n_trial=10,
        timelimit=0.5,
        callbacks=[callback],
        optimized_variables=variables[:1],
    )
    assert all(
        var.value() == value for var, value in zip(variables[1:], non_optimized_values)
    )


def test_OptunaCmaEsSearch_available(
    prob, prob_only_continuous, prob_with_const, prob_qp, prob_nonlinear, prob_perm
):
    solver = Solver(algo="OptunaCmaEs")
    assert solver.available(prob) == True
    assert solver.available(prob_only_continuous) == True
    assert solver.available(prob_with_const) == False
    assert solver.available(prob_qp) == False
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_perm) == False


def test_OptunaNSGAIISearch1(prob, callback):
    """test to solve problem has only objective"""
    prob.solve(solver="OptunaNSGAII", n_trial=10, timelimit=0.5, callbacks=[callback])


def test_OptunaNSGAIISearch2(prob_only_continuous, callback):
    """test to solve problem with optimized_variables"""
    variables = list(prob_only_continuous.getVariables())
    non_optimized_values = [var.value() for var in variables[1:]]
    prob_only_continuous.solve(
        solver="OptunaNSGAII",
        n_trial=10,
        timelimit=0.5,
        callbacks=[callback],
        optimized_variables=variables[:1],
    )
    assert all(
        var.value() == value for var, value in zip(variables[1:], non_optimized_values)
    )


def test_OptunaNSGAIISearch3(prob_qp, callback):
    prob_qp.solve(
        solver="OptunaNSGAII", n_trial=10, timelimit=0.5, callbacks=[callback]
    )


def test_OptunaNSGAIISearch4(prob_nonlinear, callback):
    prob_nonlinear.solve(
        solver="OptunaNSGAII", n_trial=10, timelimit=0.5, callbacks=[callback]
    )


def test_OptunaNSGAIISearch_available(
    prob, prob_only_continuous, prob_with_const, prob_qp, prob_nonlinear, prob_perm
):
    solver = Solver(algo="OptunaNSGAII")
    assert solver.available(prob) == True
    assert solver.available(prob_only_continuous) == True
    assert solver.available(prob_with_const) == True
    assert solver.available(prob_qp) == True
    assert solver.available(prob_nonlinear) == True
    assert solver.available(prob_perm) == False


def test_HyperoptSearch1(prob, callback):
    """test to solve problem has only objective"""
    prob.solve(solver="Hyperopt", n_trial=10, timelimit=0.5, callbacks=[callback])


def test_HyperoptSearch2(prob_ising, callback):
    """test to solve ising problem"""
    prob_ising.solve(solver="Hyperopt", n_trial=10, timelimit=0.5, callbacks=[callback])


def test_HyperoptSearch3(prob_only_continuous, callback):
    """test to solve problem with optimized_variables"""
    variables = list(prob_only_continuous.getVariables())
    non_optimized_values = [var.value() for var in variables[1:]]
    prob_only_continuous.solve(
        solver="Hyperopt",
        n_trial=10,
        timelimit=0.5,
        callbacks=[callback],
        optimized_variables=variables[:1],
    )
    assert all(
        var.value() == value for var, value in zip(variables[1:], non_optimized_values)
    )


def test_HyperoptSearch_available(
    prob,
    prob_with_const,
    prob_qp,
    prob_nonlinear,
    prob_perm,
    prob_ising,
    prob_ising_const,
):
    solver = Solver(algo="Hyperopt")
    assert solver.available(prob) == True
    assert solver.available(prob_with_const) == False
    assert solver.available(prob_qp) == False
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_perm) == False
    assert solver.available(prob_ising) == True
    assert solver.available(prob_ising_const) == False


def test_SFLA1(prob, callback):
    """test to solve problem has only objective"""
    prob.solve(
        solver="SFLA",
        n_memeplex=5,
        n_frog_per_memeplex=10,
        n_memetic_iter=100,
        n_iter=1000,
        max_step=0.01,
        timelimit=2,
        callbacks=[callback],
    )


def test_SFLA2(prob_only_continuous, callback):
    """test to solve problem with optimized_variables"""
    variables = list(prob_only_continuous.getVariables())
    non_optimized_values = [var.value() for var in variables[1:]]
    prob_only_continuous.solve(
        solver="SFLA",
        n_memeplex=5,
        n_frog_per_memeplex=10,
        n_memetic_iter=100,
        n_iter=1000,
        max_step=0.01,
        timelimit=2,
        callbacks=[callback],
        optimized_variables=variables[:1],
    )
    assert all(
        var.value() == value for var, value in zip(variables[1:], non_optimized_values)
    )


def test_SFLA_available(prob, prob_with_const, prob_qp, prob_nonlinear, prob_perm):
    solver = Solver(algo="SFLA")
    assert solver.available(prob) == True
    assert solver.available(prob_with_const) == False
    assert solver.available(prob_qp) == False
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_perm) == False


def test_PulpSearch1(prob, callback):
    prob.solve(solver="Pulp", timelimit=0.5)


def test_PulpSearch2(prob_with_const, callback):
    prob_with_const.solve(solver="Pulp", timelimit=0.5)


def test_PulpSearch3(prob_no_obj, callback):
    prob_no_obj.solve(solver="Pulp", timelimit=0.5)


def test_PulpSearch4(prob_lp, callback):
    """test to solve problem with optimized_variables"""
    variables = list(prob_lp.getVariables())
    non_optimized_values = [var.value() for var in variables[1:]]
    prob_lp.solve(solver="Pulp", timelimit=0.5, optimized_variables=variables[:1])
    assert all(
        var.value() == value for var, value in zip(variables[1:], non_optimized_values)
    )


def test_PulpSearch_available(
    prob, prob_with_const, prob_qp, prob_nonlinear, prob_perm
):
    solver = Solver(algo="Pulp")
    assert solver.available(prob) == True
    assert solver.available(prob_with_const) == True
    assert solver.available(prob_qp) == False
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_perm) == False


def test_Pulp_available_Error(prob_nonlinear, callback):
    solver = Solver(algo="Pulp")
    solver.setParams(n_trial=10, callbacks=[callback])
    try:
        prob_nonlinear.solve(solver, timelimit=0.5)
        assert False
    except flopt.error.SolverError:
        assert True


def test_ScipySearch1(prob_only_continuous, callback):
    prob_only_continuous.solve(
        solver="Scipy", n_trial=10, timelimit=0.5, callbacks=[callback]
    )


def test_ScipySearch2(prob_with_const, callback):
    prob_with_const.solve(
        solver="Scipy", n_trial=10, timelimit=0.5, callbacks=[callback]
    )


def test_ScipySearch3(prob_with_const, callback):
    """test to solve problem with optimized_variables"""
    variables = list(prob_with_const.getVariables())
    non_optimized_values = [var.value() for var in variables[1:]]
    prob_with_const.solve(
        solver="Scipy",
        n_trial=10,
        timelimit=0.5,
        callbacks=[callback],
        optimized_variables=variables[:1],
    )
    assert all(
        var.value() == value for var, value in zip(variables[1:], non_optimized_values)
    )


def test_ScipySearch_available(
    prob,
    prob_only_continuous,
    prob_with_const,
    prob_qp,
    prob_nonlinear,
    prob_ising,
    prob_ising_const,
    prob_perm,
):
    solver = Solver(algo="Scipy")
    assert solver.available(prob) == True
    assert solver.available(prob_only_continuous) == True
    assert solver.available(prob_with_const) == True
    assert solver.available(prob_qp) == True
    assert solver.available(prob_nonlinear) == True
    assert solver.available(prob_ising) == True
    assert solver.available(prob_ising_const) == True
    assert solver.available(prob_perm) == False


def test_ScipyMilpSearch1(prob):
    prob.solve(solver="ScipyMilp", timelimit=0.5)


def test_ScipyMilpSearch2(prob_only_continuous):
    prob_only_continuous.solve(solver="ScipyMilp", timelimit=0.5)


def test_ScipyMilpSearch3(prob_with_const):
    prob_with_const.solve(solver="ScipyMilp", timelimit=0.5)


def test_ScipyMilpSearch4(prob_lp):
    prob_lp.solve(solver="ScipyMilp", timelimit=0.5)


def test_ScipyMilpSearch5(prob_lp):
    variables = list(prob_lp.getVariables())
    non_optimized_values = [var.value() for var in variables[1:]]
    prob_lp.solve(solver="ScipyMilp", timelimit=0.5, optimized_variables=variables[:1])
    assert all(
        var.value() == value for var, value in zip(variables[1:], non_optimized_values)
    )


def test_ScipyMilpSearch_available(
    prob,
    prob_only_continuous,
    prob_with_const,
    prob_lp,
    prob_qp,
    prob_nonlinear,
    prob_perm,
):
    solver = Solver(algo="ScipyMilp")
    assert solver.available(prob) == True
    assert solver.available(prob_only_continuous) == True
    assert solver.available(prob_with_const) == True
    assert solver.available(prob_lp) == True
    assert solver.available(prob_qp) == False
    assert solver.available(prob_nonlinear) == False


def test_GurobiSearch_available(
    prob,
    prob_only_continuous,
    prob_with_const,
    prob_qp,
    prob_nonlinear,
    prob_ising,
    prob_ising_const,
    prob_perm,
):
    solver = Solver(algo="Gurobi")
    assert solver.available(prob) == True
    assert solver.available(prob_only_continuous) == True
    assert solver.available(prob_with_const) == True
    assert solver.available(prob_qp) == True
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_ising) == True
    assert solver.available(prob_ising_const) == True
    assert solver.available(prob_perm) == False


def test_GurobiSearch1(prob_only_continuous, callback):
    prob_only_continuous.solve(solver="Gurobi", timelimit=0.5, callbacks=[callback])


def test_GurobiSearch2(prob_qp, callback):
    prob_qp.solve(solver="Gurobi", timelimit=0.5, callbacks=[callback])


def test_CvxoptSearch1(prob_only_continuous, callback):
    prob_only_continuous.solve(
        solver="Cvxopt", n_trial=10, timelimit=0.5, callbacks=[callback]
    )


def test_CvxoptSearch2(prob_qp, callback):
    prob_qp.solve(solver="Cvxopt", n_trial=10, timelimit=0.5, callbacks=[callback])


def test_CvxoptSearch3(prob_qp, callback):
    """test to solve problem with optimized_variables"""
    variables = list(prob_qp.getVariables())
    variables.sort(key=lambda v: v.name)
    non_optimized_values = [var.value() for var in variables[1:]]
    prob_qp.solve(
        solver="Cvxopt",
        n_trial=10,
        timelimit=0.5,
        callbacks=[callback],
        optimized_variables=variables[:1],
    )
    assert all(
        var.value() == value for var, value in zip(variables[1:], non_optimized_values)
    )


def test_CvxoptSearch4(prob_qp, callback):
    """test to solve problem with optimized_variables"""
    variables = list(prob_qp.getVariables())
    variables.sort(key=lambda v: v.name, reverse=True)
    non_optimized_values = [var.value() for var in variables[1:]]
    prob_qp.solve(
        solver="Cvxopt",
        n_trial=10,
        timelimit=0.5,
        callbacks=[callback],
        optimized_variables=variables[:1],
    )
    assert all(
        var.value() == value for var, value in zip(variables[1:], non_optimized_values)
    )


def test_AmplifySearch_available(
    prob,
    prob_only_continuous,
    prob_with_const,
    prob_qp,
    prob_nonlinear,
    prob_ising,
    prob_ising_const,
    prob_perm,
):
    solver = Solver(algo="Amplify")
    assert solver.available(prob) == False
    assert solver.available(prob_only_continuous) == False
    assert solver.available(prob_with_const) == False
    assert solver.available(prob_qp) == False
    assert solver.available(prob_nonlinear) == False
    assert solver.available(prob_ising) == True
    assert solver.available(prob_ising_const) == True
    assert solver.available(prob_perm) == False


def test_AmplifySearch1(prob_ising, callback, request):
    token = request.config.getoption("amplify_token")
    if token is None:
        return
    solver = Solver(algo="Amplify")
    solver.setParams(token=token)
    prob_ising.solve(solver, timelimit=1, msg=True)


def test_AmplifySearch2(prob_ising_const, callback, request):
    token = request.config.getoption("amplify_token")
    if token is None:
        return
    solver = Solver(algo="Amplify")
    solver.setParams(token=token)
    prob_ising_const.solve(solver, timelimit=1, msg=True)


def test_CvxoptSearch1(prob_only_continuous, callback):
    prob_only_continuous.solve(
        solver="Cvxopt", n_trial=10, timelimit=0.5, callbacks=[callback]
    )


def test_CvxoptpSearch2(prob_qp, callback):
    prob_qp.solve(solver="Cvxopt", n_trial=10, timelimit=0.5, callbacks=[callback])


def test_CvxoptpSearch3(callback):
    x = Variable("x", 1, 4, "Continuous")
    prob_qp = Problem(name="issue72")
    prob_qp += x * x
    prob_qp.solve(solver="Cvxopt", n_trial=10, msg=True, callbacks=[callback])


def test_CvxoptSearch4(prob_qp, callback):
    """test to solve problem with optimized_variables"""
    variables = list(prob_qp.getVariables())
    non_optimized_values = [var.value() for var in variables[1:]]
    prob_qp.solve(
        solver="Cvxopt",
        n_trial=10,
        timelimit=0.5,
        callbacks=[callback],
        optimized_variables=variables[:1],
    )
    assert all(
        var.value() == value for var, value in zip(variables[1:], non_optimized_values)
    )


def test_AutoSearch1(prob, callback):
    prob.solve(solver="auto", timelimit=0.5, callbacks=[callback])


def test_AutoSearch2(prob_with_const, callback):
    prob_with_const.solve(solver="auto", timelimit=0.5, callbacks=[callback])


def test_AutoSearch3(prob_ising, callback):
    prob_ising.solve(solver="auto", timelimit=0.5, callbacks=[callback])


def test_AutoSearch4(prob_with_const, callback):
    prob_with_const.solve(solver="auto", timelimit=0.5, callbacks=[callback])


def test_AutoSearch5(prob_qp, callback):
    prob_qp.solve(solver="auto", timelimit=0.5, callbacks=[callback])


def test_AutoSearch6(prob_perm, callback):
    prob_perm.solve(solver="auto", timelimit=0.5, callbacks=[callback])


def test_AutoSearch_available(
    prob, prob_with_const, prob_qp, prob_nonlinear, prob_perm
):
    solver = Solver(algo="auto")
    assert solver.available(prob) == True
    assert solver.available(prob_with_const) == True
    assert solver.available(prob_qp) == True
    assert solver.available(prob_nonlinear) == True
    assert solver.available(prob_perm) == True


def test_solver_log(prob, callback):
    solver = Solver(algo="Random")
    solver.setParams(n_trial=10, callbacks=[callback])
    status, log = prob.solve(solver, timelimit=0.2)
    print(log.getLog())
    print(log[0])
    fig, ax = log.plot(show=False)


def test_solver_log_add(prob, callback):
    solver = Solver(algo="Random")
    solver.setParams(n_trial=10, callbacks=[callback])
    status1, log1 = prob.solve(solver, timelimit=0.2)
    status2, log2 = prob.solve(solver, timelimit=0.2)
    add_len = len(log1 + log2)
    assert add_len == len(log1) + len(log2)

    log1 += log2
    assert len(log1) == add_len


def test_estimate_problem_type(
    prob,
    prob_only_continuous,
    prob_with_const,
    prob_qp,
    prob_nonlinear,
    prob_ising,
    prob_ising_const,
    prob_perm,
):
    estimate_problem_type(prob)
    estimate_problem_type(prob_only_continuous)
    estimate_problem_type(prob_with_const)
    estimate_problem_type(prob_qp)
    estimate_problem_type(prob_nonlinear)
    estimate_problem_type(prob_ising)
    estimate_problem_type(prob_ising_const)
    estimate_problem_type(prob_perm)

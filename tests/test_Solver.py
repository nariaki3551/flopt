from flopt import Variable, Problem, Solver, Solver_list, CustomExpression


test_all = True
test_SFLA = True

# Problem without constraint
a = Variable('a', 0, 1, 'Integer')
b = Variable('b', 1, 2, 'Continuous')
c = Variable('c', 1, 3, 'Continuous')
prob = Problem(name='Test')
prob += a + b + c

# Problem with constraint
prob_with_const = Problem(name='TestC')
prob_with_const += a + b + c
prob_with_const += a + b >= 2

# Permutation Problem
p = Variable('p', 0, 4, 'Permutation')
prob_perm = Problem('TestP')
def obj(p):
    return p[-1] - p[0]
prob_perm +=  CustomExpression(obj, [p])


# callback
def callback(solutions, best_solution, best_obj_value):
    pass

def test_Solver_list():
    Solver_list()

def test_RandomSearch1():
    solver = Solver(algo='RandomSearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob.solve(solver, timelimit=1)

def test_RandomSearch2():
    solver = Solver(algo='RandomSearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob_perm.solve(solver, timelimit=1)

def test_2Opt():
    solver = Solver(algo='2-Opt')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob_perm.solve(solver, timelimit=1)

def test_OptunaTPESearch():
    solver = Solver(algo='OptunaTPESearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob.solve(solver, timelimit=1)

def test_OptunaCmaEsSearch():
    solver = Solver(algo='OptunaCmaEsSearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob.solve(solver, timelimit=1)

def test_HyperoptTPESearch():
    solver = Solver(algo='HyperoptTPESearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob.solve(solver, timelimit=1)

def test_SFLA():
    solver = Solver(algo="SFLA")
    solver.setParams(
        n_memeplex=5, n_frog_per_memeplex=10, n_memetic_iter=100,
        n_iter=1000, max_step=0.01, msg=True, callbacks=[callback],
    )
    prob.solve(solver=solver, timelimit=10)

def test_PulpSearch1():
    solver = Solver(algo='PulpSearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob.solve(solver, timelimit=1)

def test_PulpSearch2():
    solver = Solver(algo='PulpSearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob_with_const.solve(solver, timelimit=1)

def test_ScipySearch1():
    solver = Solver(algo='ScipySearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob.solve(solver, timelimit=1)

def test_ScipySearch2():
    solver = Solver(algo='ScipySearch')
    solver.setParams(n_trial=10, callbacks=[callback])
    prob_with_const.solve(solver, timelimit=1)


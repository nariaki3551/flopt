from flopt import Variable, Problem, Solver, Solver_list


test_all = False

test_solver_list = False
test_common = False
test_SFLA = True

if test_solver_list or test_all:
    def test_Solver_list():
        solver_list = Solver_list()

if test_common or test_all:
    def test_common():
        # Variables
        a = Variable('a', lowBound=0, upBound=1, cat='Integer')
        b = Variable('b', lowBound=1, upBound=2, cat='Continuous')
        c = Variable('c', lowBound=1, upBound=3, cat='Continuous')
        prob = Problem(name='Test')
        prob += 2*(3*a+b)*c**2+3

        solver_list = Solver_list()

        for algo in Solver_list():
            def test_Solver_params():
                solver = Solver(algo=algo)
                solver.setParams(n_trial=10)
                prob.solve(solver, timelimit=1)

            def test_Solver_callbacks():
                def callback(solutions, best_solution, best_obj_value):
                    pass
                solver = Solver(algo=algo)
                solver.setParams(n_trial=10, callbacks=[callback])
                prob.solve(solver, timelimit=1)

if test_SFLA or test_all:
    def test_SFLA_1():
        # Variables
        prob = Problem(name='Test')
        x = Variable('x', lowBound=0, upBound=100, cat='Continuous')
        y = Variable('y', lowBound=0, upBound=100, cat='Continuous')
        prob += (x+y)/(x-1)*(y-1)

        solver = Solver(algo="SFLA")
        solver.setParams(n_memeplex=5, n_frog_per_memeplex=10,
                         n_memetic_iter=100, n_iter=1000, max_step=0.01, msg=True)
        prob.solve(solver=solver, timelimit=10)


from flopt import Variable, Problem, Solver

__doc__ = """
This is a sample code of a Basis usage of flopt
"""
DISPLAY = False


# Variables
a = Variable("a", lowBound=0, upBound=1, cat="Integer")
b = Variable("b", lowBound=1, upBound=2, cat="Continuous")
c = Variable("c", lowBound=1, upBound=3, cat="Continuous")

print(a)  # display information of variable a

# 1. Minimize
# Problem
# in this case optimal solution (a, b, c) = (0, 1, 1), and objective value = 5
prob = Problem(name="Test")
prob += 2 * (3 * a + b) * c**2 + 3

# Solver
solver = Solver(algo="RandomSearch")
solver.setParams(n_trial=1000)  # setting of the hyper parameters
status, log = prob.solve(solver, msg=True)  # run solver to solve the problem

if DISPLAY:
    log.plot()  # display logs during solve

# display the result, incumbent solution
print()
print("obj value", prob.getObjectiveValue())
print("a", a.value())
print("b", b.value())
print("c", c.value())


# 2. Maximize
# Problem
# in this case optimal solution (a, b, c) = (1, 2, 3), and objective value = 93
prob = Problem(name="Test", sense="maximize")
prob.setObjective(2 * (3 * a + b) * c * c + 3)

# Solver
solver = Solver(algo="RandomSearch")
solver.setParams({"n_trial": 1000})  # setting of the hyper parameters
status, log = prob.solve(solver, msg=True)  # run solver to solve the problem

if DISPLAY:
    log.plot()  # display logs during solve

# display the result, incumbent solution
print()
print("obj value", prob.getObjectiveValue())
print("a", a.value())
print("b", b.value())
print("c", c.value())

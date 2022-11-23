from flopt import Variable, Problem, CustomExpression, Solver

__doc__ = """
This is a sample code of "CustomExpression"
"""

# Variables
a = Variable("a", lowBound=0, upBound=1, cat="Integer")
b = Variable("b", lowBound=1, upBound=2, cat="Continuous")
c = Variable("c", lowBound=1, upBound=3, cat="Continuous")

print(a)  # display information of variable a

# user defined func
from math import sin, cos


def user_func(a, b, c):
    return (0.7 * a + 0.3 * cos(b) ** 2 + 0.1 * sin(c)) * c


custom_obj = CustomExpression(func=user_func, args=[a, b, c])


# 1. Minimize
# Problem
prob = Problem(name="Test")
prob += custom_obj

# Solver
# in this case optimal solution (a, b, c) = (0, 1, 1), and objective value = 0.4
solver = Solver(algo="Random")
solver.setParams(n_trial=1000)  # setting of the hyper parameters
status, log = prob.solve(solver, msg=True)  # run solver to solve the problem

# log.plot()  # display logs during solve

# display the result, incumbent solution
print()
print("obj value", prob.getObjectiveValue())
print("a", a.value())
print("b", b.value())
print("c", c.value())


# 1. Minimize
# Problem
# custom_obj * c
prob = Problem(name="Test")
prob += custom_obj * c

# Solver
# in this case optimal solution (a, b, c) = (0, 1, 1), and objective value = 0.4
solver = Solver(algo="Random")
solver.setParams({"n_trial": 1000})  # setting of the hyper parameters
status, log = prob.solve(solver, msg=True)  # run solver to solve the problem

# log.plot()  # display logs during solve

# display the result, incumbent solution
print()
print("obj value", prob.getObjectiveValue())
print("a", a.value())
print("b", b.value())
print("c", c.value())


# 2. Maximize
# Problem
prob = Problem(name="Test", sense="Maximize")
prob += custom_obj

# Solver
# in this case optimal solution (a, b, c) = (1, 2, 3), and objective value = 2.2
solver = Solver(algo="Random")
solver.setParams(n_trial=1000)  # setting of the hyper parameters
status, log = prob.solve(solver, msg=True)  # run solver to solve the problem

# log.plot()  # display logs during solve

# display the result, incumbent solution
print()
print("obj value", prob.getObjectiveValue())
print("a", a.value())
print("b", b.value())
print("c", c.value())

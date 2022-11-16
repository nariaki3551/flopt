import numpy as np

from flopt import Variable, Problem, CustomExpression, Solver

__doc__ = """
This is a sample code of "TSP"
"""
DISPLAY = False

# number of cities
N = 100
# distance matrix; D[i][j] the distance between i and j
D = np.random.rand(N, N)
for i in range(N):
    D[i, i] = 0

# Variables
perm = Variable("perm", lowBound=0, upBound=N - 1, cat="Permutation")

# Object
def tsp_dist(perm):
    distance = 0
    for head, tail in zip(perm, perm[1:] + [perm[0]]):
        distance += D[head][tail]
    return distance


tsp_obj = CustomExpression(func=tsp_dist, arg=[perm])


# Problem
prob = Problem(name="Test")
prob += tsp_obj


# 1. Random Search
solver = Solver(algo="Random")
solver.setParams(timelimit=2)  # setting of the hyper parameters
status, log = prob.solve(solver, msg=True)  # run solver to solve the problem
if DISPLAY:
    fig, ax = log.plot(show=False, label="Random")

print("random-search obj value", prob.getObjectiveValue())
print("perm", perm.value())


# 1. 2-Opt
perm.setRandom()

solver = Solver(algo="2-Opt")
solver.setParams(timelimit=2)  # setting of the hyper parameters
status, log = prob.solve(solver, msg=True)  # run solver to solve the problem
if DISPLAY:
    fig, ax = log.plot(show=True, label="2-Opt", fig=fig, ax=ax)

print()
print("2-opt obj value", prob.getObjectiveValue())
print("perm", perm.value())

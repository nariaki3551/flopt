Permutation Optimization Problem
================================

Overview
--------

::

  minimize the total distance of routing the cities.
  s.t.     We have to visit every city one time.
           we have the distance between all the cities.

This is one of the most famous optimization problem, Traveling Salesman Problem (TSP).
There are two ways of solving TSP:

1. optimize the permutations directly
2. optimize the permutations using the Linear Programming (LP) method.

The former method is shown in the following.

.. code-block:: python

  from flopt import Variable, Problem, Solver

  # We have the distance matrix D, and the number of city is N

  # Variables
  perm = Variable('perm', lowBound=0, upBound=N-1, cat='Permutation')

  # Object
  def tsp_dist(perm):
      distance = 0
      for head, tail in zip(perm, perm[1:]+[perm[0]]):
          distance += D[head][tail]  # D is the distance matrix
      return distance
  tsp_obj = CustomObject(func=tsp_dist, variables=[perm])

  # Problem
  prob = Problem(name='TSP')
  prob += tsp_obj

  # Solver
  solver = Solver(algo='2-Opt')
  solver.setParams(timelimit=60)
  prob.solve(solver, msg=True)

  # Result
  print(perm.value())


Permutation Variable
--------------------

We can get a variable representing the permutation by setting `cat='Permuation'`.
It contains a list of [lowBound, ... , upBound].

.. code-block:: python

  # Variables
  perm = Variable('perm', lowBound=0, upBound=3, cat='Permutation')
  >> perm.value()
  >> [3, 1, 2, 0]  # permutation is shuffled

  perm = Variable('perm', lowBound=0, upBound=3, iniValue=list(range(0, 4)), cat='Permutation')
  >> perm.value()
  >> [0, 1, 2, 3]


Objective function
------------------

Then, we prepare the objective function. We can represent the TSP objective function by the function `tsp_dist` using the distance matrix D (D[i][j] is the distance between city i and j).
In order for Solver to solve this problem, we use CustomObject to transform this function. We use Variable `perm` as the argument of the function `tsp_dist`.

.. code-block:: python

  def tsp_dist(perm):
      distance = 0
      for head, tail in zip(perm, perm[1:]+[perm[0]]):
          distance += D[head][tail]  # D is the distance matrix
      return distance
  tsp_obj = CustomObject(func=tsp_dist, variables=[perm])


Solver
------

The algorithms for the permutation variables are `RandoSearch` and `2-Opt`.
In most cases, `2-Opt` is better.

.. code-block:: python

  # Solver
  solver = Solver(algo='2-Opt')
  solver.setParams(timelimit=60)
  prob.solve(solver, msg=True)


Result
------

The result of the solver is reflected in Variable `perm`.
We can get the best solution by `perm.value()`

.. code-block:: python

  print(perm.value())



Travelling salesman problem
===========================

Overview
--------

::

  minimize the total distance of routing the cities.
  s.t.     We have to visit every city one time.
           we have the distance between all the cities.

This is one of the most famous optimization problem, Traveling Salesman Problem (TSP).
There are several ways of solving TSP:

1. optimize the permutations directly
2. optimize the permutations using the Linear Programming (LP) method
3. and others

Optimize the permutations directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The first method is shown in the following.

.. code-block:: python

  import flopt

  # We have the distance matrix D, and the number of city is N
  N = 4
  D = [
      [0.0, 3.0, 2.0, 1.0],
      [2.0, 0.0, 1.0, 1.0],
      [1.0, 3.0, 0.0, 4.0],
      [1.0, 1.0, 2.0, 1.0],
  ]

  # Variables
  perm = flopt.Variable("perm", lowBound=0, upBound=N-1, cat="Permutation")

  # Problem
  prob = flopt.Problem(name="TSP")

  # Object
  def tsp_dist(perm):
      distance = 0
      for head, tail in zip(perm, perm[1:]+[perm[0]]):
          distance += D[head][tail]  # D is the distance matrix
      return distance
  tsp_obj = flopt.CustomExpression(func=tsp_dist, args=[perm])
  prob += tsp_obj

  # solver setting
  solver = flopt.Solver(algo="2-Opt")
  solver.setParams(timelimit=3)

  # run solver
  prob.solve(solver, msg=True)

  # Result
  print("result", perm.value())



Permutation Variable
~~~~~~~~~~~~~~~~~~~~

We can get a variable representing the permutation by setting `cat="Permuation"`.
It contains a list of [lowBound, ... , upBound].

.. code-block:: python

  # Variables
  perm = Variable("perm", lowBound=0, upBound=3, cat="Permutation")
  >> perm.value()
  >> [3, 1, 2, 0]  # permutation is shuffled

  perm = Variable("perm", lowBound=0, upBound=3, ini_value=list(range(0, 4)), cat="Permutation")
  >> perm.value()
  >> [0, 1, 2, 3]


Objective function
~~~~~~~~~~~~~~~~~~

Then, we prepare the objective function. We can represent the TSP objective function by the function `tsp_dist` using the distance matrix D (D[i][j] is the distance between city i and j).
In order for Solver to solve this problem, we use CustomExpression to transform this function. We use `perm` Variable as the argument of the function `tsp_dist`.

.. code-block:: python

  def tsp_dist(perm):
      distance = 0
      for head, tail in zip(perm, perm[1:]+[perm[0]]):
          distance += D[head][tail]  # D is the distance matrix
      return distance
  tsp_obj = flopt.CustomExpression(func=tsp_dist, args=[perm])


Solver
~~~~~~

The algorithms for the permutation variables are `RandoSearch` and `2-Opt`.
In most cases, `2-Opt` is better.

.. code-block:: python

  # Solver
  solver = flopt.Solver(algo="2-Opt")
  solver.setParams(timelimit=3)
  prob.solve(solver, msg=True)  # run solver


Result
~~~~~~

The result of the solver is reflected in Variable `perm`.
We can get the best solution by `.value()`

.. code-block:: python

  print(perm.value())


Optimize using the Linear Programming (LP) method
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TSP can be formulated as Linear programming (LP).
Miller-Tucker-Zemlin formulation is a major method for solving TSP as LP.
The following code is an example code of Miller-Tucker-Zemlin formulation.

.. code-block:: python

  import flopt

  # We have the distance matrix D, and the number of city is N
  N = 4
  D = [
      [0.0, 3.0, 2.0, 1.0],
      [2.0, 0.0, 1.0, 1.0],
      [1.0, 3.0, 0.0, 4.0],
      [1.0, 1.0, 2.0, 1.0],
  ]

  # Variables
  cities = list(range(N))
  x = flopt.Variable.matrix("x", N, N, cat="Binary")
  np.fill_diagonal(x, 0)
  u = flopt.Variable.array("u", N, lowBound=0, upBound=N - 1, cat="Continuous")

  # Problem
  prob = flopt.Problem(name=f"TSP_LP")

  # Objective
  tsp_obj = flopt.sum(D * x)  # sum(D[i, j] * x[i, j] for all i, j)
  prob += tsp_obj

  # Constraints (flow condition)
  for i in cities:
      prob += flopt.sum(x[i, :]) == 1
      prob += flopt.sum(x[:, i]) == 1

  # COnstraints (remove subtour)
  for i, j in itertools.combinations(cities, 2):
      prob += u[j] >= u[i] + 1 - N * (1 - x[i, j])
      if i != 0:
          prob += u[i] >= u[j] + 1 - N * (1 - x[j, i])
  prob += u[0] == 0

  # run solver
  prob.solve(timelimit=3, msg=True)

  # Result
  print("result", perm.value())


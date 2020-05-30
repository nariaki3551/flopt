Satisfiability Problem
======================

Overview
--------

::

  minimize 0
  s.t.     c1 = x0 or x1
           c2 = x0 or not x1
           c3 = not x0 or x1
           c4 = not x0 or not x1
           x0, x1 is Binary

This optimization problem is a kind of the `SAT problem`.
This problem can be formulated using `flopt` as follows,

.. code-block:: python

  from flopt import Variable, Problem, Solver

  # literals
  x0 = Variable('x0', cat='Binary')
  x1 = Variable('x1', cat='Binary')

  # clauses
  c1 = x0 | x1
  c2 = x0 | ~x1
  c3 = ~x0 | x1
  c4 = ~x0 | ~x1

  prob = Problem('Sat', sense='satisfiability')

  solver = Solver(algo='RandomSearch')
  prob.solve(solver, timelimit=10, msg=True)

  print('value x0', x0.value())
  print('value x1', x1.value())
  for clause in clauses:
      print(clause)


Objective function
------------------

Like SAT, if we only want to know whether a feasible solution exists or not,
we input sense to 'satisfiability'.

.. code-block:: python

  prob = Problem('Sat', sense='satisfiability')

Result
------

The results of the solver are reflected in the problem and variable objects.

.. code-block:: python

  print('value x0', x0.value())
  print('value x1', x1.value())
  for clause in clauses:
      print(clause)


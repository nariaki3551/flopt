Max Satisfiability Problem
==========================

Overview
--------

::

  maximize (c1+2*c2+3*c3+4*c4)
  s.t.     c1 = x0 or x1
           c2 = x0 or not x1
           c3 = not x0 or x1
           c4 = not x0 or not x1
           x0, x1 is Binary

This optimization problem is a kind of the `weighted MAX-SAT problem`.
This problem can be formulated using `flopt` as follows,

.. code-block:: python

  import flopt 

  # literals
  x0 = flopt.Variable("x0", cat="Binary")
  x1 = flopt.Variable("x1", cat="Binary")

  # clauses
  c1 = x0 | x1
  c2 = x0 | ~x1
  c3 = ~x0 | x1
  c4 = ~x0 | ~x1

  clauses = [c1, c2, c3, c4]
  weights = [1, 2, 3, 4]
  obj = flopt.dot(clauses, weights)

  prob = flopt.Problem("MaxSat", sense="Maximize")
  prob += obj

  prob.solve(timelimit=2, msg=True)

  print("value x0", x0.value())
  print("value x1", x1.value())
  for clause in clauses:
    print(f"{clause} = {clause.value()}")


Literals
--------

We declear potitive literals using *Variable*.

.. code-block:: python

  # literals
  x0 = flopt.Variable("x0", cat="Binary")
  x1 = flopt.Variable("x1", cat="Binary")

`~x0` represents a non positive literal of `x0`, e.g. if `x0=0` then `~x0=1`.


Clauses
-------

`or` operation of literal is `|`.

.. code-block:: python

  c1 = x0 | x1    # x0 or x1
  c2 = x0 | ~x1   # x0 or (not x1)


Objective function
------------------

We can create the objective function by arithmetic operation of literals or cluses, or the CustomExpression.
For example, :math:`(c_1+2c_2+3c_3+4c_4)` can be formulated as follows.

.. code-block:: python

  clauses = [c1, c2, c3, c4]
  weights = [1, 2, 3, 4]
  obj = flopt.dot(clauses, weights)


Result
------

The results of the solver are reflected in the problem and variable objects.

.. code-block:: python

  print("value x0", x0.value())
  print("value x1", x1.value())
  for clause in clauses:
      print(clause)


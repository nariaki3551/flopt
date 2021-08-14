(Non) Linear Problem with Constraints
=====================================

Overview
--------

::

  minimize  2*(3*a+b**2) + 3
  s.t.      a*b >= 2
            0 <= a <= 1, a is integer
            1 <= b <= 2, b is continuous


This optimization problem is a kind of the *mixed integer constrained non-linear programming with constraints*.
This problem can be formulated using `flopt` as follows,

.. code-block:: python

  from flopt import Variable, Problem, Solver

  # variables
  a = Variable(name='a', 0, 1, cat='Integer')
  b = Variable(name='b', 1, 2, cat='Continuous')

  # problem
  prob = Problem(name='Test')
  prob += 2*(3*a+b**2)   # set the objective function
  prob += a*b >= 2  # add constraint

  # solver
  solver = Solver(algo='ScipySearch')  # select the heuristic algorithm
  prob.solve(solver, timelimit=10, msg=True)    # run solver

  # get best solution
  print('obj value', prob.getObjectiveValue())
  print('a', a.value())
  print('b', b.value())


Constraint
----------

We set constraints to the problem using `+=` operation or `.addConstraint`.


.. code-block:: python

  prob = Problem(name='Test', sense='minimize')
  prob += a*b >= 2   # set the objective function
  # prob.addConstraint(a*b >= 2)   # same above

We can set equality and inequality constraint.

.. code-block:: python

  prob += a*b >= 2
  prob += a*b == 2
  prob += a*b <= 2

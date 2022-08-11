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
  a = Variable("a", 0, 1, cat="Continuous")
  b = Variable("b", 1, 2, cat="Continuous")

  # problem
  prob = Problem(name="Test")
  prob += 2*(3*a+b**2)  # set the objective function
  prob += a*b >= 2      # add constraint

  # solver setting
  solver = Solver(algo="ScipySearch")  # select the scipy function

  # run solver
  prob.solve(solver, timelimit=10, msg=True)

  # get best solution
  print("obj value", prob.getObjectiveValue())
  print("a", a.value())
  print("b", b.value())


Constraint
----------

We can set constraints to the problem using `+=` operation or `.addConstraint`.


.. code-block:: python

  prob = Problem(name="Test", sense="minimize")
  prob += a*b >= 2   # set the objective function
  # prob.addConstraint(a*b >= 2)   # same above

Equality and inequality constraints are able to be used.

.. code-block:: python

  prob += a*b >= 2
  prob += a*b == 2
  prob += a*b <= 2


To show the added constraints, we use `.show()` method.

.. code-block:: python

  # variables
  a = Variable("a", 0, 1, cat="Continuous")
  b = Variable("b", 1, 2, cat="Continuous")

  # problem
  prob = Problem(name="Test")
  prob += 2*(3*a+b**2)  # set the objective function
  prob += a*b >= 2      # add constraint
  prob += a+b >= 2      # add constraint

  print(prob.show())
  >>> Name: Show Test
  >>>   Type         : Problem
  >>>   sense        : minimize
  >>>   objective    : 2*3*a+b^2
  >>>   #constraints : 2
  >>>   #variables   : 2 (Continuous 2)
  >>>
  >>>   C 0, name None, a*b-2 >= 0
  >>>   C 1, name None, a+b-2 >= 0


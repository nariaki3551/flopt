(Non) Linear Problem
====================

Overview
--------

::

  minimize  2*(3*a+b)*c**2 + 3
  s.t.      0 <= a <= 1, a is integer
            1 <= b <= 2, b is continuous
            1 <= c <= 3, c is continuous


This optimization problem is a kind of the *mixed integer constrained non-linear programming*.
This problem can be formulated using `flopt` as follows,

.. code-block:: python

  from flopt import Variable, Problem, Solver

  # variables
  a = Variable(name='a', lowBound=0, upBound=1, cat='Integer')
  b = Variable(name='b', lowBound=1, upBound=2, cat='Continuous')
  c = Variable(name='c', lowBound=1, upBound=3, cat='Continuous')

  # problem
  prob = Problem(name='Test')
  prob += 2*(3*a+b)*c**2+3   # set the objective function

  # solver
  solver = Solver(algo='RandomSearch')  # select the heuristic algorithm
  solver.setParams(n_trial=1000)  # setting of the parameters
  prob.solve(solver, msg=True)    # run solver

  # get best solution
  print('obj value', prob.getObjectiveValue())
  print('a', a.value())
  print('b', b.value())
  print('c', c.value())


Variable
--------

We declear variables using :doc:`../api_reference/Variable`.

::

  0 <= a <= 1, a is integer
  1 <= b <= 2, b is continuous
  1 <= c <= 3, c is continuous

In flopt, we denote these as

.. code-block:: python

  a = Variable(name='a', lowBound=0, upBound=1, cat='Integer')
  b = Variable(name='b', lowBound=1, upBound=2, cat='Continuous')
  c = Variable(name='c', lowBound=1, upBound=3, cat='Continuous')

, more simplify

.. code-block:: python

  a = Variable(name='a', 0, 1, 'Integer')
  b = Variable(name='b', 1, 2, 'Continuous')
  c = Variable(name='c', 1, 3, 'Continuous')

If we want to set an initial value into each variable, we use `ini_value` option.

.. code-block:: python

  b = Variable(name='b', 1, 2, 'Continuous', ini_value=1.5)


Problem
-------

We can create the objective function by arithmetic operation of variables for example :math:`2(3a+b)c^2 + 3`, or the CustomExpression.

We set the object function in *Problem* using `+=` operation or `.setObjective` function.

.. code-block:: python

  prob = Problem(name='Test', sense='minimize')
  prob += 2*(3*a+b)*c**2+3   # set the objective function
  # prob.setObjective(2*(3*a+b)*c**2+3)   # same above

If we want to solve a maximize problem, then we set `sense='maximize'` (default is sense=minimize).

.. code-block:: python

  prob = Problem(name='Test', sense='maximize')


Solver
------

We select algorithm from :doc:`../solvers/index` for the problem. We can see the list of available solvers by `flopt.Solver_list()`.

.. code-block:: python

  solver = Solver(algo='RandomSearch')  # select the heuristic algorithm
  solver.setParams(n_trial=1000, timelimit=3600)  # setting of the parameters
  # solver.setParams({'n_trial'; 1000, 'timelimit': 3600})  # same above

Solve
-----

.. code-block:: python

  prob.solve(solver, msg=True)    # run solver



Result
------

The results of the solver are reflected in the problem and variable objects.

- `getObjectiveValue()` in problem shows the objective value of the best solution solver found.<br>

- `value()` in variable shows the value of variable of the best solution.

.. code-block:: python

  print('obj value', prob.getObjectiveValue())
  print('a', a.value())
  print('b', b.value())
  print('c', c.value())

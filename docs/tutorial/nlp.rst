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

  from flopt import Variable, Problem, Solver, Value

  # variables
  a = Variable(name="a", lowBound=0, upBound=1, cat="Integer")
  b = Variable(name="b", lowBound=1, upBound=2, cat="Continuous")
  c = Variable(name="c", lowBound=1, upBound=3, cat="Continuous")

  # problem
  prob = Problem(name="Test")

  # set objective function
  prob += 2*(3*a+b)*c**2+3

  # solver setting
  solver = Solver(algo="RandomSearch")  # select the random search algorithm
  solver.setParams(n_trial=1000)  # set the parameters for solver

  # run solver
  prob.solve(solver, msg=True)

  # get best solution
  print("obj value", prob.getObjectiveValue())
  print("a", Value(a))  # or a.value()
  print("b", Value(b))
  print("c", Value(c))


Variable
--------

We declear variables using :doc:`../api_reference/Variable`.

::

  0 <= a <= 1, a is integer
  1 <= b <= 2, b is continuous
  1 <= c <= 3, c is continuous

In flopt, we denote these as

.. code-block:: python

  a = Variable(name="a", lowBound=0, upBound=1, cat="Integer")    # is equal to Variable("a", 0, 1, flopt.VarInteger)
  b = Variable(name="b", lowBound=1, upBound=2, cat="Continuous") # is equal to Variable("b", 1, 2, "Continuous")
  c = Variable(name="c", lowBound=1, upBound=3, cat="Continuous") # is equal to Variable("c", 1, 3, flopt.VarContinuous)

We can set an initial value to each variable by `ini_value` option.

.. code-block:: python

  b = Variable("b", 1, 2, "Continuous", ini_value=1.5)


Problem
-------

In flont, we can create the objective function by arithmetic operation of variables for example :math:`2(3a+b)c^2 + 3`, or :doc:`../api_reference/CustomExpression`.

We set the object function to *Problem* using `+=` operation or `.setObjective` function.

.. code-block:: python

  prob = Problem(name="Test", sense="minimize")
  prob += 2*(3*a+b)*c**2+3   # set the objective function
  # prob.setObjective(2*(3*a+b)*c**2+3)   # same above

When we solve a maximize problem, we set `sense="Maximize"` (default is sense=minimize).

.. code-block:: python

  prob = Problem(name="Test", sense="Maximize")


Solver
------

We select algorithm from :doc:`../solvers/index` for the problem. We can see the list of available solvers by `flopt.Solver_list()`.

.. code-block:: python

  solver = Solver(algo="RandomSearch")  # select the heuristic algorithm
  solver.setParams(n_trial=1000, timelimit=3600)  # setting of the parameters
  # solver.setParams({"n_trial"; 1000, "timelimit": 3600})  # same above

Solve
-----

.. code-block:: python

  prob.solve(solver, msg=True)  # run solver



Result
------

The result of the solver is reflected in Problem and Variable objects.

- `getObjectiveValue()` in problem shows the objective value of the best solution solver found.

- `Value()` in variable shows the value of variable of the best solution.

.. code-block:: python

  print("obj value", prob.getObjectiveValue())
  print("a", Value(a))  # or a.value()
  print("b", Value(b))
  print("c", Value(c))


Solver Profiling
----------------

You can easily see the transition of the incumbent solution.

.. code-block:: python

  status, logs = prob.solve(solver, msg=True)  # run solver
  fig, ax = logs.plot(label="objective value of best solution", marker="o")

.. image:: https://cdn-ak.f.st-hatena.com/images/fotolife/i/inarizuuuushi/20220826/20220826103011.png

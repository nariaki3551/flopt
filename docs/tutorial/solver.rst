Solvers
=======

Users can use some third-party solvers and solvers implemented in flopt.
We can see all available solvers by `flopt.Solver_list()`.

.. code-block:: python

  import flopt

  flopt.Solver_list()
  >>> ['RandomSearch',
  >>>  '2-Opt',
  >>>  'OptunaTPESearch',
  >>>  'OptunaCmaEsSearch',
  >>>  'HyperoptTPESearch',
  >>>  'SFLA',
  >>>  'PulpSearch',
  >>>  'ScipySearch',
  >>>  'ScipyMilpSearch',
  >>>  'CvxoptQpSearch',
  >>>  'auto']

All available solvers for user defined problem can be shown by as follows.

.. code-block:: python

  a = flopt.Variable("a", 0, 1, cat="Continuous")
  b = flopt.Variable("b", 1, 2, cat="Continuous")
  
  prob = flopt.Problem(name="Test")
  prob += 2*a + 3*b
  prob += a + b >= 1

  flopt.allAvailableSolvers(prob)
  >>> ['PulpSearch',
  >>>  'ScipySearch',
  >>>  'ScipyMilpSearch',
  >>>  'CvxoptQpSearch',
  >>>  'auto']


You can specify the available solver by declaring solver object.

.. code-block:: python

  solver = flopt.Solver(algo="ScipySearch")
  prob.solve(solver=solver)



AutoSolver
^^^^^^^^^^

Flopt provides *AutoSolver*.
We specify the AutoSolver, flopt select the appropriate solver for the problem.


.. code-block:: python

  solver = flopt.Solver(algo="auto")


When we check which solver is selected, we execute `solver.select(prob).name`.


.. code-block:: python

  solver = flopt.Solver(algo="auto")
  solver.setParams(timelimit=1)
  solver.select(prob).name
  >>> 'ScipyMilpSearch'

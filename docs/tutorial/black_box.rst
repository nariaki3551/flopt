Black Box Optimization Problem
==============================

Overview
-------------

::

  minimize  simulator(a, b)
  s.t.      0 <= a <= 1, a is integer
            1 <= b <= 2, b is continuous


This optimization problem is a kind of the *mixed integer constrained Black Box Optimization programming*.
This problem can be formulated using `flopt` as follows,

.. code-block:: python

  from flopt import Variable, CustomObject, Problem, Solver

  # variables
  a = Variable(name='a', lowBound=0, upBound=1, cat='Integer')
  b = Variable(name='b', lowBound=1, upBound=2, cat='Continuous')

  # objective function
  def simulator(a, b):
      return simulator_func(a, b)

  custom_obj = CustomObject(func=user_func, variables=[a, b])

  # problem
  prob = Problem(name='CustomObject')
  prob += custom_obj

  # solver
  solver = Solver(algo='RandomSearch')
  solver.setParams(timelimit=60)
  prob.solve(solver, msg=true)


  # get best solution
  print('obj value', prob.getObjectiveValue())
  print('a', a.value())
  print('b', b.value())


CustomObject
------------

We can create a complex objective function using *CustomObject*.
We input two items to create CustomObject.
One is the python function,
and another is the list (or tuple or iterator) of variables in the same order as the arguments in the function.

.. code-block:: python

  def simulator(a, b):
      return simulator_func(a, b)

  custom_obj = CustomObject(func=user_func, variables=[a, b])


When the objective function with a list of variables as arguments, we have the following.

.. code-block:: python

  def obj(x):
      return sin(x[0])+cos(x[1])

  x0 = Variable(name='x0', lowBound=1, upBound=2, cat='Continuous')
  x1 = Variable(name='x1', lowBound=1, upBound=2, cat='Continuous')
  x = [x0, x1]
  custom_obj = CustomObject(func=obj, variables=[x])

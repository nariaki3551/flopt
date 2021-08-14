LP
==

::

  minimize  c^T x + C
  s.t.      Ax <= b
            lb <= x <= ub
            x_i is integer or real variablce


This optimization problem is called Linear Programming (LP) Problem.
For example, the following problem is one of the LP.

.. code-block:: python

  from flopt import Variable, Problem

  # variables
  a = Variable(name='a', lowBound=0, upBound=1, cat='Integer')
  b = Variable(name='b', lowBound=1, upBound=2, cat='Continuous')
  c = Variable(name='c', lowBound=1, upBound=3, cat='Continuous')

  # problem
  prob = Problem(name='LP')
  prob += a + b + c + 2
  prob += a + b <= 2
  prob += b - c <= 3

  print(prob)
  >>> Name: None
  >>>   Type         : Problem
  >>>   sense        : minimize
  >>>   objective    : a+b+c+2
  >>>   #constraints : 2
  >>>   #variables   : 3 (Continuous 2, Integer 1)

flopt to LP
-----------

We can convert this into Lp form as follows.

.. code-block:: python

  from flopt.convert import flopt_to_lp
  lp = flopt_to_lp(prob)  # obtain LP form

  print(lp.c)
  >>> [1. 1. 1.]
  print(lp.C)
  >>> 2.0
  print(lp.A)
  >>> [[ 1.  0.  1.]
  >>>  [ 1. -1.  0.]]
  print(lp.b)
  >>> [2. 3.]
  print(lp.lb)
  >>> [1 1 0]
  print(lp.ub)
  >>> [2 3 1]
  print(lp.x)
  >>> [VarElement("b", 1, 2, 1.5) VarElement("c", 1, 3, 2.0)
  >>>  VarElement("a", 0, 1, 0)]

To obtain the variable type, we use `.getType()` function.

.. code-block:: python

  for var in lp.x:
      print(var.getType())
  >>> VarInteger
  >>> VarContinuous
  >>> VarContinuous


LP to flopt
-----------

.. code-block:: python

  # make Lp model
  c = [1, 1, 1]
  C = 2
  A = [[1, 0, 1],
       [1, -1, 0]]
  b = [2, 3]
  lb = [1, 1, 0]
  ub = [2, 3, 1]
  var_types=['Binary', 'Continuous', 'Continuous']

  from flopt.convert import lp_to_flopt
  prob = lp_to_flopt(A, b, c, C, lb, ub, var_types)
  print(prob)
  >>> Name: None
  >>>   Type         : Problem
  >>>   sense        : minimize
  >>>   objective    : x0+x1+x2+2
  >>>   #constraints : 2
  >>>   #variables   : 3 (Binary 1, Continuous 2)

  print(prob.constraints)
  >>> [Constraint(Expression(x0+x2, 2, -), le, None),
  >>> Constraint(Expression(x0+(x1*-1)+0, 3, -), le, None)]

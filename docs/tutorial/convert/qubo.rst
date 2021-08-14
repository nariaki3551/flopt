QUBO
====

::

  minimize  x^T Q x + C
            x_i is in {0, 1}


This optimization problem is called QUBO model.

flopt to QUBO
-------------

For example, the following problem is one of the QUBO using `Binary` variables.

.. code-block:: python

  from flopt import Variable, Problem

  # Variables
  a = Variable('a', cat='Binary')
  b = Variable('b', cat='Binary')

  # Problem
  prob = Problem()
  prob += 1 - a * b - a

  print(prob)
  >>> Name: None
  >>>   Type         : Problem
  >>>   sense        : minimize
  >>>   objective    : 1-a*b-a
  >>>   #constraints : 0
  >>>   #variables   : 2 (Binary 2)


We can convert this into QUBO form as follows.

.. code-block:: python

  from flopt.convert import flopt_to_qubo
  qubo = flopt_to_qubo(prob)

  print(qubo.Q)
  >>> [[-1. -1.]
  >>>  [ 0.  0.]]
  print(qubo.C)
  >>> 1.00000000000000
  print(qubo.x)
  >>> [Variable(a, cat="Binary", iniValue=0)
  >>>  Variable(b, cat="Binary", iniValue=0)]


We can convert evan problem includes `Spin` variables.

.. code-block:: python

  from flopt import Variable, Problem

  # Variables
  a = Variable('a', cat='Spin')
  b = Variable('b', cat='Binary') # Binary variable

  # Problem
  prob = Problem()
  prob += 1 - a * b - a

  print(prob)
  >>> Name: None
  >>>   Type         : Problem
  >>>   sense        : minimize
  >>>   objective    : 1-(a*b)-a
  >>>   #constraints : 0
  >>>   #variables   : 2 (Binary 1, Spin 1)


By `.toBinary()`, we can see the objective function when all the variables are transformed to `Binary`.

.. code-block:: python

  print(prob.obj.toBinary().name)
  >>> '1-a*(b_b*2-1)-a'

`b_b` is the binary variable converted from `b`.

.. code-block:: python

  from flopt.convert import flopt_to_qubo
  qubo = flopt_to_qubo(prob)

  print(qubo.Q)
  >>> [[ 0. -2.]
  >>>  [ 0.  0.]]
  print(qubo.C)
  >>> 1.00000000000000
  print(qubo.x)
  >>> [Variable(a, cat="Binary", iniValue=0)
  >>>  Variable(b_b, cat="Binary", iniValue=0)]



QUBO to flopt
--------------

.. code-block:: python


  # make ising
  Q = [[-1, -1],
       [0, 0]]
  C = 1.0

  from flopt.convert import qubo_to_flopt
  prob = qubo_to_flopt(Q, C)

  print(prob)
  >>> Name: None
  >>>   Type         : Problem
  >>>   sense        : minimize
  >>>   objective    : (-s0)*s1-s0+1.0
  >>>   #constraints : 0
  >>>   #variables   : 2 (Binary 2)


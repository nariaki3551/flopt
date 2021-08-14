Ising
=====

::

  minimize  - x^T J x - h^T x + C
            x_i is in {-1, 1}


This optimization problem is called Ising model.

flopt to Ising
--------------

For example, the following problem is one of the Ising using `Spin` variables.

.. code-block:: python

  from flopt import Variable, Problem

  # Variables
  a = Variable('a', cat='Spin')
  b = Variable('b', cat='Spin')

  # Problem
  prob = Problem()
  prob += 1 - a * b - a

  print(prob)
  >>> Name: None
  >>>   Type         : Problem
  >>>   sense        : minimize
  >>>   objective    : 1-a*b-a
  >>>   #constraints : 0
  >>>   #variables   : 2 (Spin 2)


We can convert this into Ising form as follows.

.. code-block:: python

  from flopt.convert import flopt_to_ising
  ising = flopt_to_ising(prob)  # obtain Ising form

  print(ising.J)
  >>> [[0. 1.]
  >>>  [0. 0.]]
  print(ising.h)
  >>> [1. 0.]
  print(ising.C)
  >>> 1.0
  print(ising.x)
  >>> [Variable(a, cat="Spin", iniValue=-1) Variable(b, cat="Spin", iniValue=-1)]


We can convert evan problem includes `Binary` variables.

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


By `.toSpin()`, we can see the objective function when all the variables are transformed to `Spin`.

.. code-block:: python

  print(prob.obj.toSpin().name)
  >>> '1-a*((b_s+1)*0.5)-a'

`b_s` is the spin variable converted from `b`.

.. code-block:: python

  from flopt.convert import flopt_to_ising
  ising = flopt_to_ising(prob)

  print(ising.J)
  >>> [[0. 1.]
  >>>  [0. 0.]]
  print(ising.h)
  >>> [1.5 0. ]
  print(ising.C)
  >>> 1.0
  print(ising.x)
  >>> [Variable(a, cat="Spin", iniValue=-1)
  >>>  Variable(b_s, cat="Spin", iniValue=-1)]


Ising to flopt
--------------

.. code-block:: python

  # make ising model
  J = [[0, 1],
       [0, 0]]
  h = [1, 0]
  C = 1

  from flopt.convert import ising_to_flopt
  prob = ising_to_flopt(J, h, C)

  print(prob)
  >>> Name: None
  >>>   Type         : Problem
  >>>   sense        : minimize
  >>>   objective    : -s0*s1-s0+1
  >>>   #constraints : 0
  >>>   #variables   : 2 (Spin 2)

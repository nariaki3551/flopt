Quadratic Unconstrainted Binary Programming (QUBO)
==================================================

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

  from flopt.convert import QuboStructure
  qubo = QuboStructure.fromFlopt(prob)


To show the contents of lp,

.. code-block:: python

  print(qubo.show())
  >>> QuboStructure
  >>> x.T.dot(Q).dot(x) + C
  >>>
  >>> #x
  >>> 2
  >>>
  >>> Q
  >>> [[-1. -1.]
  >>>  [ 0.  0.]]
  >>>
  >>> C
  >>> 1.0
  >>>
  >>> x
  >>> [Variable("a", cat="Binary", ini_value=0)
  >>>  Variable("b", cat="Binary", ini_value=0)]


We can convert evan problem includes `Spin` variables.



QUBO to flopt
--------------

.. code-block:: python

  # make ising
  Q = [[-1, -1],
       [0, 0]]
  C = 1.0

  from flopt.convert import QuboStructure
  prob = QuboStructure(Q, C).toFlopt()

  print(prob)
  >>> Name: None
  >>>   Type         : Problem
  >>>   sense        : minimize
  >>>   objective    : -1*(x_0*x_1)-x_0+1.0
  >>>   #constraints : 0
  >>>   #variables   : 2 (Binary 2)

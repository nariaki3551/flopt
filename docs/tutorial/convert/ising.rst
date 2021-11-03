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

  from flopt.convert import IsingStructure
  ising = IsingStructure.fromFlopt(prob)


To show the contents of ising structure,

.. code-block:: python

  print(ising.show())
  >>> IsingStructure
  >>> - x.T.dot(J).dot(x) - h.T.dot(x) + C
  >>>
  >>> #x
  >>> 2
  >>>
  >>> J
  >>> [[-0.  1.]
  >>>  [-0. -0.]]
  >>>
  >>> h
  >>> [ 1. -0.]
  >>>
  >>> C
  >>> 1
  >>>
  >>> x
  >>> [Variable("a", cat="Spin", ini_value=1)
  >>>  Variable("b", cat="Spin", ini_value=1)]


We can convert flopt to ising even if the problem includes binary variable.
Binary variables are automatically replaced to spin variable.

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

  from flopt.convert import IsingStructure
  ising = IsingStructure.fromFlopt(prob)

  print(ising.show())
  >>> IsingStructure
  >>> - x.T.dot(J).dot(x) - h.T.dot(x) + C
  >>>
  >>> #x
  >>> 2
  >>>
  >>> J
  >>> [[-0.   0.5]
  >>>  [-0.  -0. ]]
  >>>
  >>> h
  >>> [ 1.5 -0. ]
  >>>
  >>> C
  >>> 1.0
  >>>
  >>> x
  >>> [Variable("a", cat="Spin", ini_value=-1)
  >>>  Variable("b_s", cat="Spin", ini_value=-1)]


`b_s` is the spin variable as `b_s = 2 b - 1`.


Convert QUBO
^^^^^^^^^^^^

To convert this problem as QUBO formulation, we use `.toQubo()` function.

.. code-block:: python

  ising.toQubo()    # convert ising to QUBO

  print(ising.toQubo().toFlopt().show())  # for show cleary ising.toQubo()
  >>> Name: None
  >>>   Type         : Problem
  >>>   sense        : minimize
  >>>   objective    : -4.0*(a_b*b_b)+(2.0*b_b)+1.0
  >>>   #constraints : 0
  >>>   #variables   : 2 (Binary 2)


`a_b` is the binary variable as `a_b = (1+a)/2`.
In addition, `.toQp()`, `.toLp()` are also available.



Ising to flopt
--------------

.. code-block:: python

  # make ising model
  J = [[0, 1],
       [0, 0]]
  h = [1, 0]
  C = 1

  from flopt.convert import IsingStructure
  prob = IsingStructure(J, h, C).toFlopt()

  print(prob.show())
  >>> Name: None
  >>>   Type         : Problem
  >>>   sense        : minimize
  >>>   objective    : -x_0*x_1-x_0+1
  >>>   #constraints : 0
  >>>   #variables   : 2 (Spin 2)


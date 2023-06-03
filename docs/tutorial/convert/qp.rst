Quadratic Programming (QP)
==========================

::

  minimize  x^T Q x + c^T x + C
  s.t.      Gx <= h
            Ax == b
            lb <= x <= ub
            x_i is integer or continuous variablce


This optimization problem is called Quadratic Programming (QP) Problem.
For example, the following problem is one of the QP.

.. code-block:: python

  from flopt import Variable, Problem

  # Variables
  a = Variable('a', lowBound=0, upBound=1, cat='Integer')
  b = Variable('b', lowBound=1, upBound=2, cat='Continuous')
  c = Variable('c', lowBound=1, upBound=3, cat='Continuous')

  # Problem
  prob = Problem()
  prob += a*a + a*b + b + c + 2
  prob += a + b <= 2
  prob += b - c == 3

  prob.show()
  >>> Name: None
  >>>   Type         : Problem
  >>>   sense        : minimize
  >>>   objective    : a*a+(a*b)+b+c+2
  >>>   #constraints : 2
  >>>   #variables   : 3 (Continuous 2, Integer 1)
  >>>
  >>>   C 0, name None, a+b-2 <= 0
  >>>   C 1, name None, b-c-3 == 0


flopt to QP
-----------

We convert problem modeled in flopt into QP form as follows.

.. code-block:: python

  from flopt.convert import QpStructure
  qp = QpStructure.fromFlopt(prob)


To show the contents of qp, use `.show()` method.
In addition, we can access each element using attributes of QpStructure, for example, `qp.Q`.

.. code-block:: python

  print(qp.show())
  >>> QpStructure
  >>> obj  1/2 x.T.dot(Q).dot(x) + c.T.dot(x) + C
  >>> s.t. Gx <= h
  >>>      Ax == b
  >>>      lb <= x <= ub
  >>>
  >>> #x
  >>> 3
  >>>
  >>> Q
  >>> [[0. 0. 0.]
  >>>  [0. 0. 1.]
  >>>  [0. 1. 2.]]
  >>>
  >>> c
  >>> [1. 1. 0.]
  >>>
  >>> C
  >>> 2
  >>>
  >>> G
  >>> [[0. 1. 1.]]
  >>>
  >>> h
  >>> [2.]
  >>>
  >>> A
  >>> [[-1.  1.  0.]]
  >>>
  >>> b
  >>> [3.]
  >>>
  >>> lb
  >>> [1. 1. 0.]
  >>>
  >>> ub
  >>> [3. 2. 1.]
  >>>
  >>> x
  >>> [Variable("c", 1, 3, "Continuous", 2.0)
  >>>  Variable("b", 1, 2, "Continuous", 1.5) Variable("a", 0, 1, "Integer", 0)]




Formulation with only equal constraints
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can obtain the formulaton with only eqaual constraints by `.toAllEq()`


::

  minimize  c^T x + C
  s.t.      Ax == b
            lb <= x <= ub
            x_i is integer or continuous variablce


.. code-block:: python

  qp.toAllEq()


Formulation with only non-equal constraints
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can obtain the formulaton with only non-eqaual constraints by `.toAllNeq()`


::

  minimize  c^T x + C
  s.t.      Gx <= h
            lb <= x <= ub
            x_i is integer or continuous variablce


.. code-block:: python

  qp.toAllNeq()



QP to flopt
-----------

.. code-block:: python

  # make QP model
  Q = [[1, 2, 0],
       [2, 2, 1],
       [0, 1, 0]]
  c = [1, 1, 1]
  C = 2
  A = [[1, 0, 1],
       [1, -1, 0]]
  b = [2, 3]
  lb = [1, 1, 0]
  ub = [2, 3, 1]
  types='Continuous'

  from flopt.convert import QpStructure
  prob = QpStructure(Q, c, C, A=A, b=b, lb=lb, ub=ub, types=types).toFlopt()

  prob.show()
  >>> Name: None
  >>>   Type         : Problem
  >>>   sense        : minimize
  >>>   objective    : 0.5*(x_0^2)+(2.0*(x_0*x_1))+x_0+(x_1^2)+(x_1*x_2)+x_1+x_2+2
  >>>   #constraints : 2
  >>>   #variables   : 3 (Continuous 3)
  >>>
  >>>   C 0, name None, x_0+x_2-2.0 == 0
  >>>   C 1, name None, x_0-x_1-3.0 == 0

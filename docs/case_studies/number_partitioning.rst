Number Partitioning
===================

We will solver the number partitioning problem.
We try to find the partion of numbers A to two groups, B and C,
such that summation of B and that of C are equal.

.. code-block:: python

    # list of numbers
    A = [10, 8, 7, 9]

We use Spin variables :math:`s_i` to formulate this problem.
A spin variable only takes +1 or -1.
:math:`s_i = +1` represents that element A[i] is belong to B, and :math:`s_i = -1` represents element A[i] is belong to C.
In that time, the difference of the summation of elemements in B and that of C can be calculated by :math:`\sum_i a_i s_i`.

Hence, we can obtain the desired partitioning by optimizing the spin variables to take minimum value of :math:`(\sum_i a_i s_i)^2`.

::

    min  sum( a_i s_i ) ^ 2
    s.t. s_i in {-1, 1}


In flopt, we model the problem as follows.

.. code-block:: python

    import flopt

    # create variables
    s = flopt.Variable.array("s", len(A), cat="Spin")

    # create problem
    prob = flopt.Problem("Number Partitioning")

    # set objective function
    prob += flopt.dot(s, A) ** 2

    print(prob)
    >>> Name: Number Partitioning
    >>>   Type         : Problem
    >>>   sense        : minimize
    >>>   objective    : (10*s_0+(8*s_1)+(7*s_2)+(9*s_3))^2
    >>>   #constraints : 0
    >>>   #variables   : 4 (Spin 4)


Solving using RandomSearch
--------------------------

We search the optimal solution by RandomSearch.
This is a simple sampling algorithm, which repeats to assigne random values to all variables in one search phase.

.. code-block:: python

    # solve until obtain the solution
    # whose objective value is lower than or equal to 0
    prob.solve(solver="Random", msg=True, lowerbound=0)

    print("s", flopt.Value(s))
    >>> s [1 -1 1 -1]


We succeeded to obtain the optimal solution.


Solving using LP Search
-----------------------

Flopt provides the powerful **problem linearize** mecanism, so if the defined problem can be linearized then we can use the LP solvers to obtain the optimal solution.
First, we linearize the objective function and constraints by flopt.convert.linearize.
To linearize the product of spin variables, flopt replace spin variables to binary variables and add slack variables and constrains.

.. code-block:: python

    from flopt.convert import linearize

    linearize(prob)

    prob.show()
    >>> Name: Number Partitioning
    >>>   Type         : Problem
    >>>   sense        : minimize
    >>>   objective    : 640*mul_0+(560*mul_1)+(720*mul_2)+(448*mul_3)+(576*mul_4)+(504*mul_5)-(960*s_0_b)-(832*s_1_b)-(756*s_2_b)-(900*s_3_b)+1156
    >>>   #constraints : 18
    >>>   #variables   : 10 (Binary 10)
    >>>
    >>>   C 0, name for_mul_0_1, mul_0-s_0_b <= 0
    >>>   C 1, name for_mul_0_2, mul_0-s_1_b <= 0
    >>>   C 2, name for_mul_0_3, mul_0-s_0_b-s_1_b+1 >= 0
    >>>   C 3, name for_mul_1_1, mul_1-s_0_b <= 0
    >>>   C 4, name for_mul_1_2, mul_1-s_2_b <= 0
    >>>   C 5, name for_mul_1_3, mul_1-s_0_b-s_2_b+1 >= 0
    >>>   C 6, name for_mul_2_1, mul_2-s_0_b <= 0
    >>>   C 7, name for_mul_2_2, mul_2-s_3_b <= 0
    >>>   C 8, name for_mul_2_3, mul_2-s_0_b-s_3_b+1 >= 0
    >>>   C 9, name for_mul_3_1, mul_3-s_1_b <= 0
    >>>   C 10, name for_mul_3_2, mul_3-s_2_b <= 0
    >>>   C 11, name for_mul_3_3, mul_3-s_1_b-s_2_b+1 >= 0
    >>>   C 12, name for_mul_4_1, mul_4-s_1_b <= 0
    >>>   C 13, name for_mul_4_2, mul_4-s_3_b <= 0
    >>>   C 14, name for_mul_4_3, mul_4-s_1_b-s_3_b+1 >= 0
    >>>   C 15, name for_mul_5_1, mul_5-s_2_b <= 0
    >>>   C 16, name for_mul_5_2, mul_5-s_3_b <= 0
    >>>   C 17, name for_mul_5_3, mul_5-s_2_b-s_3_b+1 >= 0

Then, we solve it.

.. code-block:: python

    prob.solve(solver="auto")

    print("s", Value(s))
    >>> s [1 -1 1 -1]


Conversion to other formulations of number partitioning
-------------------------------------------------------


By using flopt.convert methods, we can obtain the structure data for another formulation of the number partitioning.


QP
^^

.. code-block:: python

    from flopt import Variable, Problem, Dot
    from flopt.convert import QpStructure

    s = Variable.array("x", len(A), cat="Spin")
    prob = Problem("Number Partitioning")
    prob += Dot(s, A) ** 2

    # create QpStructure after binarize problem
    flopt.convert.binarize(prob)
    qp = QpStructure.fromFlopt(prob)

    print(qp.show())
    >>> QpStructure
    >>> obj  1/2 x.T.dot(Q).dot(x) + c.T.dot(x) + C
    >>> s.t. Gx <= h
    >>>      Ax == b
    >>>      lb <= x <= ub
    >>>
    >>> #x
    >>> 4
    >>>
    >>> Q
    >>> [[  0. 112. 160. 144.]
    >>>  [112.   0. 140. 126.]
    >>>  [160. 140.   0. 180.]
    >>>  [144. 126. 180.   0.]]
    >>>
    >>> c
    >>> [0. 0. 0. 0.]
    >>>
    >>> C
    >>> 294
    >>>
    >>> G
    >>> None
    >>>
    >>> h
    >>> None
    >>>
    >>> A
    >>> None
    >>>
    >>> b
    >>> None
    >>>
    >>> lb
    >>> [-1. -1. -1. -1.]
    >>>
    >>> ub
    >>> [1. 1. 1. 1.]
    >>>
    >>> x
    >>> [Variable("x_1", cat="Spin", ini_value=1)
    >>>  Variable("x_2", cat="Spin", ini_value=-1)
    >>>  Variable("x_0", cat="Spin", ini_value=-1)
    >>>  Variable("x_3", cat="Spin", ini_value=-1)]



LP
^^

.. code-block:: python

    from flopt.convert import LpStructure
    lp = LpStructure.fromFlopt(prob)

    print(lp.show())
    >>> LpStructure
    >>> obj  c.T.dot(x) + C
    >>> s.t. Gx <= h
    >>>      Ax == b
    >>>      lb <= x <= ub
    >>>
    >>> #x
    >>> 10
    >>>
    >>> c
    >>> [ 504.  560. -900.  720.  576. -756.  640. -960.  448. -832.]
    >>>
    >>> C
    >>> 1156.0
    >>>
    >>> G
    >>> [[ 0.  0.  0.  0.  0.  0.  1. -1.  0.  0.]
    >>>  [ 0.  0.  0.  0.  0.  0.  1.  0.  0. -1.]
    >>>  [-0. -0. -0. -0. -0. -0. -1.  1. -0.  1.]
    >>>  [ 0.  1.  0.  0.  0.  0.  0. -1.  0.  0.]
    >>>  [ 0.  1.  0.  0.  0. -1.  0.  0.  0.  0.]
    >>>  [-0. -1. -0. -0. -0.  1. -0.  1. -0. -0.]
    >>>  [ 0.  0.  0.  1.  0.  0.  0. -1.  0.  0.]
    >>>  [ 0.  0. -1.  1.  0.  0.  0.  0.  0.  0.]
    >>>  [-0. -0.  1. -1. -0. -0. -0.  1. -0. -0.]
    >>>  [ 0.  0.  0.  0.  0.  0.  0.  0.  1. -1.]
    >>>  [ 0.  0.  0.  0.  0. -1.  0.  0.  1.  0.]
    >>>  [-0. -0. -0. -0. -0.  1. -0. -0. -1.  1.]
    >>>  [ 0.  0.  0.  0.  1.  0.  0.  0.  0. -1.]
    >>>  [ 0.  0. -1.  0.  1.  0.  0.  0.  0.  0.]
    >>>  [-0. -0.  1. -0. -1. -0. -0. -0. -0.  1.]
    >>>  [ 1.  0.  0.  0.  0. -1.  0.  0.  0.  0.]
    >>>  [ 1.  0. -1.  0.  0.  0.  0.  0.  0.  0.]
    >>>  [-1. -0.  1. -0. -0.  1. -0. -0. -0. -0.]]
    >>>
    >>> h
    >>> [0. 0. 1. 0. 0. 1. 0. 0. 1. 0. 0. 1. 0. 0. 1. 0. 0. 1.]
    >>>
    >>> A
    >>> None
    >>>
    >>> b
    >>> None
    >>>
    >>> lb
    >>> [0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
    >>>
    >>> ub
    >>> [1. 1. 1. 1. 1. 1. 1. 1. 1. 1.]
    >>>
    >>> x
    >>> [Variable("mul_5", cat="Binary", ini_value=0)
    >>>  Variable("mul_1", cat="Binary", ini_value=0)
    >>>  Variable("x_3_b", cat="Binary", ini_value=0)
    >>>  Variable("mul_2", cat="Binary", ini_value=0)
    >>>  Variable("mul_4", cat="Binary", ini_value=0)
    >>>  Variable("x_2_b", cat="Binary", ini_value=0)
    >>>  Variable("mul_0", cat="Binary", ini_value=0)
    >>>  Variable("x_0_b", cat="Binary", ini_value=0)
    >>>  Variable("mul_3", cat="Binary", ini_value=0)
    >>>  Variable("x_1_b", cat="Binary", ini_value=1)]


Ising
^^^^^

.. code-block:: python

    from flopt.convert import IsingStructure
    ising = IsingStructure.fromFlopt(prob)

    print(ising.show())
    >>> IsingStructure
    >>> - x.T.dot(J).dot(x) - h.T.dot(x) + C
    >>>
    >>> #x
    >>> 4
    >>>
    >>> J
    >>> [[  -0. -160. -140. -180.]
    >>>  [  -0.   -0. -112. -144.]
    >>>  [  -0.   -0.   -0. -126.]
    >>>  [  -0.   -0.   -0.   -0.]]
    >>>
    >>> h
    >>> [-0. -0. -0. -0.]
    >>>
    >>> C
    >>> 294.0
    >>>
    >>> x
    >>> [Variable("x_0", cat="Spin", ini_value=-1)
    >>>  Variable("x_1", cat="Spin", ini_value=1)
    >>>  Variable("x_2", cat="Spin", ini_value=-1)
    >>>  Variable("x_3", cat="Spin", ini_value=-1)]


Qubo
^^^^

.. code-block:: python

    from flopt.convert import QuboStructure
    qubo = QuboStructure.fromFlopt(prob)

    print(qubo.show())
    >>> QuboStructure
    >>> x.T.dot(Q).dot(x) + C
    >>>
    >>> #x
    >>> 4
    >>>
    >>> Q
    >>> [[-960.  640.  560.  720.]
    >>>  [   0. -832.  448.  576.]
    >>>  [   0.    0. -756.  504.]
    >>>  [   0.    0.    0. -900.]]
    >>>
    >>> C
    >>> 1156.0
    >>>
    >>> x
    >>> [Variable("x_0_b", cat="Binary", ini_value=0)
    >>>  Variable("x_1_b", cat="Binary", ini_value=1)
    >>>   Variable("x_2_b", cat="Binary", ini_value=0)
    >>>    Variable("x_3_b", cat="Binary", ini_value=0)] ] ] ]]


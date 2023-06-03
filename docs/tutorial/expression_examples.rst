Expression Examples
===================

.. code-block:: python

  import flopt


1. :math:`f = \sum_i x_i`
-------------------------

.. code-block:: python

  x = flopt.Variable.array("x", 4)
  f = flopt.sum(x)

  print(f)
  >>> Name: x_0+x_1+x_2+x_3
  >>> Type    : Normal
  >>> Value   : 0.0


2. :math:`f = \sum_i \sum_j x_i x_j`
------------------------------------

.. code-block:: python

  import itertools

  x = flopt.Variable.array("x", 4)
  f = flopt.sum(xi * xj for xi, xj in itertools.product(x, x))

  print(f)
  >>> Name: x_0*x_0+(x_0*x_1)+(x_0*x_2)+(x_0*x_3)+(x_1*x_0)+(x_1*x_1)+(x_1*x_2)+(x_1*x_3)+(x_2*x_0)+(x_2*x_1)+(x_2*x_2)+(x_2*x_3)+(x_3*x_0)+(x_3*x_1)+(x_3*x_2)+(x_3*x_3)
  >>>   Type    : Normal
  >>>   Value   : 0.0

.. code-block:: python

  x = flopt.Variable.array("x", (4, 1))
  f = flopt.sum(x.dot(x.T))

  print(f)
  >>> Name: x_0_0*x_0_0+(x_0_0*x_1_0)+(x_0_0*x_2_0)+(x_0_0*x_3_0)+(x_1_0*x_0_0)+(x_1_0*x_1_0)+(x_1_0*x_2_0)+(x_1_0*x_3_0)+(x_2_0*x_0_0)+(x_2_0*x_1_0)+(x_2_0*x_2_0)+(x_2_0*x_3_0)+(x_3_0*x_0_0)+(x_3_0*x_1_0)+(x_3_0*x_2_0)+(x_3_0*x_3_0)
  >>>   Type    : Normal
  >>>   Value   : 0.0


3. :math:`f = \sum_i \left( \sum_j x_{ij} -1 \right) ^2`
--------------------------------------------------------

.. code-block:: python

  x = flopt.Variable.matrix("x", 2, 2)
  f = flopt.sum((flopt.sum(xi) - 1) ** 2 for xi in x)

  print(f)
  >>> Name: (x_0_0+x_0_1-1)^2+((x_1_0+x_1_1-1)^2)
  >>>   Type    : Normal
  >>>   Value   : 2.0


4. :math:`f = \sum_{i \neq j}x_i x_j`
-------------------------------------

.. code-block:: python

  import itertools

  x = flopt.Variable.array("x", 4)
  f = flopt.sum(xi * xj for xi, xj in itertools.combinations(x, 2))

  print(f)
  >>> Name: x_0*x_1+(x_0*x_2)+(x_0*x_3)+(x_1*x_2)+(x_1*x_3)+(x_2*x_3)
  >>>   Type    : Normal
  >>>   Value   : 0.0


5. :math:`f = \prod_i x_i`
--------------------------

.. code-block:: python

  x = flopt.Variable.array("x", 4)
  f = flopt.prod(x)

  print(f)
  >>> Name: ((x_0*x_1)*x_2)*x_3
  >>>   Type    : Normal
  >>>   Value   : 0.0


Show a calculation graph
------------------------

You can easily see the calculation graphs of expressions by using `get_dot_graph`


.. code-block:: python

  import itertools

  x = flopt.flopt.Variable.array("x", 3)
  f = flopt.flopt.sum(xi * xj for xi, xj in itertools.product(x, x))
  save_path = "tmp.txt"
  flopt.get_dot_graph(f, save_path)

In addition, you execute Graphviz command.

.. code-block:: shell

  dot tmp.txt -T png -o tmp.png

.. image:: https://cdn-ak.f.st-hatena.com/images/fotolife/i/inarizuuuushi/20220826/20220826103019.png

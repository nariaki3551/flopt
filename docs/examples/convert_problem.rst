Convert Problem
================

We can convert the expand expression to the Ising model form.

.. code-block:: python

   a = Variable(name='a', iniValue=1, cat='Binary')
   b = Variable(name='b', iniValue=1, cat='Binary')
   c = Variable(name='c', iniValue=1, cat='Binary')
   import numpy as np

   # make Ising model
   x = np.array([a, b, c])
   J = np.array([
       [1, 2, 1],
       [0, 1, 1],
       [0, 0, 3]
   ])
   h = np.array([1, 2, 0])
   obj = (x.T).dot(J).dot(x) + (h.T).dot(x)

   print(obj)
   >>> Name: (((a*(((a*1)+(b*0))+(c*0)))+(b*(((a*2)+(b*1))+(c*0))))+(c*(((a*1)+(b*1))+(c*3))))+(((a*1)+(b*2))+(c*0))
   >>>   Type    : Expression
   >>>   Value   : 20.25
   >>>   Degree  : 2


Obj is long expression, seeing Name of obj.
We can check the obj is able to be converted Ising form.

.. code-block:: python

   print(obj.isIsing())
   >>> True

And, we convert this obj to Ising model form, as follows.

.. code-block:: python

   # obj to Ising model
   ising = obj.toIsing()

   print(ising.J)
   >>> array([[3., 1., 1.],
   >>>        [0., 1., 2.],
   >>>        [0., 0., 1.]])

   print(ising.h)
   >>> array([[0.],
   >>>        [1.],
   >>>        [2.]])

   print(ising.variable_list)
   >>> [VarElement("c", 1, 3, 1), VarElement("a", 0, 1, -1), VarElement("b", 1, 2, 1)]

obj = x^TJx + h^Tx, where x = variable_list.

We set the solution we obtain to the obj, as follows.

.. code-block:: python

  solution = [1, -1, 1]
  for var, value in zip(ising.variable_list, solution):
      var.setValue(value)

  print(obj.value())
  >>> 4


Newton's method
===============

Newton's method is a kind of iterative root-finding algorithm using jacobian.
When we obtain :math:`x \in \mathbb{R}` such that :math:`f(x) = 0` where :math:`f: \mathbb{R} \to \mathbb{R}`,
newton's method updates as follows.

:math:`x_{n+1} \leftarrow x_n - \cfrac{f(x_n)}{f'(x_n)} \ (n \geq 0)` with initial point :math:`x_0`

In flopt, we can obtain the jacobian expression of expression :math:`f` by `f.jac()`.
Then we obtain the jacobian value by `f.jac().value()` or `Value(f.jac())`.

The following code obtains the root of :math:`f(x) = x^2 - 2`, so it is success that :math:`x` becomes :math:`\sqrt{2}` 

.. code-block:: python

   import flopt
   from flopt import Value

   # define f
   def f(x):
       return x * x - 2
   
   # define variable with initial value
   x = flopt.Variable("x", ini_value=5)
   
   # obtain jacobian function
   jac_fn, _ = f(x).jac()
   
   for roop in range(10):
       # update x
       x.setValue( Value(x) - Value(f(x)) / Value(jac_fn) )
       print(f'roop {roop:<4d} x = {Value(x)}')

Output of above code is here.

::

   roop 0    x = 2.7
   roop 1    x = 1.7203703703703703
   roop 2    x = 1.44145536817765
   roop 3    x = 1.414470981367771
   roop 4    x = 1.4142135857968836
   roop 5    x = 1.4142135623730951
   roop 6    x = 1.414213562373095
   roop 7    x = 1.4142135623730951
   roop 8    x = 1.414213562373095
   roop 9    x = 1.4142135623730951

We obtained the neary value of :math:`\sqrt{2}`.

Another code equivalent to above code is shown here.

.. code-block:: python

   import flopt
   from flopt import Value
   
   # define variable with initial value
   x = flopt.Variable("x", init_value=5)
   
   # define f
   f = x * x - 2
   
   # obtain jacobian function
   jac, _ = f.jac()
   
   for roop in range(10):
       # update x
       x.setValue( Value(x) - Value(f) / Value(jac) )
       print(f'roop {roop:<4d} x = {Value(x)}')

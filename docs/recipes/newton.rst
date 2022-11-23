Newton's method
===============

Newton's method for root-finding
--------------------------------

Newton's method is a kind of iterative root-finding algorithm using jacobian.
When we obtain :math:`x \in \mathbb{R}` such that :math:`f(x) = 0` where :math:`f: \mathbb{R} \to \mathbb{R}`,
newton's method updates as follows.

:math:`x_{n+1} \leftarrow x_n - \cfrac{f(x_n)}{f'(x_n)} \ (n \geq 0)` with initial point :math:`x_0`

In flopt, we can obtain the jacobian expression of expression :math:`f` by `f.jac()`.
Then we obtain the jacobian value by `f.jac().value()` or `Value(f.jac())`.

The following code obtains the root of :math:`f(x) = x^2 - 2`, so it is success that :math:`x` becomes :math:`\sqrt{2}` 

.. code-block:: python

   import flopt

   # define f
   def f(x):
       return x * x - 2
   
   # define variable with initial value
   x = flopt.Variable("x", ini_value=100)
   
   # obtain jacobian function
   jac = f(x).jac([x])
   
   for roop in range(10):
       # update x
       x.setValue((x - f(x) / jac).value())
       print(f'roop {roop},  x = {x.value()}')

Output of above code is here.

::

  roop 0,  x 50.01
  roop 1,  x 25.024996000799838
  roop 2,  x 12.552458046745901
  roop 3,  x 6.3558946949311395
  roop 4,  x 3.335281609280434
  roop 5,  x 1.967465562231149
  roop 6,  x 1.4920008896897232
  roop 7,  x 1.4162413320389438
  roop 8,  x 1.4142150140500531
  roop 9,  x 1.414213562373845

We obtained the neary value of :math:`\sqrt{2}`.

Another code equivalent to above code is shown here.

.. code-block:: python

   import flopt
   
   # define variable with initial value
   x = flopt.Variable("x", init_value=100)
   
   # define f
   f = x * x - 2
   
   # obtain jacobian function
   jac = f.jac(x)
   
   for roop in range(10):
       # update x
       x.setValue(x.value() - f.value() / jac.value())
       print(f'roop {roop},  x = {x.value()}')


Newton's method for minimizing expression
-----------------------------------------

We minimize smoothly function :math:`f` by newton's method.
Update method is as follows.

:math:`x_{n+1} \leftarrow x_n - \nabla^2 f(x_n)^{-1} \nabla f(x_n) (n \geq 0)` with initial point :math:`x_0`.

.. code-block:: python

  import flopt
  import flopt.solution
  
  import itertools
  import numpy as np
  
  x1 = flopt.Variable("x1", ini_value=0)
  x2 = flopt.Variable("x2", ini_value=3)
  x = flopt.solution.Solution([x1, x2])
  
  f = (x1 - 2) ** 4 + (x1 - 2 * x2) ** 2
  
  jac_fn = f.jac(x)
  hess_fn = f.hess(x)
  
  for i in itertools.count():
      # 1. calculate jac, hess
      # 2. search direction d
      # 3. update x
      jac, hess = jac_fn.value(), hess_fn.value()
      d = - np.dot(np.linalg.inv(hess), jac)
      x += d
      
      print("iter", i, "x", x.value(), "obj", f.value())
  
      # terminate condition
      if np.linalg.norm(jac) < 1e-4:
          break


.. image:: https://cdn-ak.f.st-hatena.com/images/fotolife/i/inarizuuuushi/20221120/20221120192625.png

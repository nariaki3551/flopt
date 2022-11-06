Iterative Search
----------------


Random Search (RandomSearch)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: https://img.shields.io/badge/Variable-any-blue.svg
.. image:: https://img.shields.io/badge/Objective-any-orange.svg
.. image:: https://img.shields.io/badge/Constraints-None-green.svg

.. autoclass:: flopt.solvers.random_search.RandomSearch


2-Opt (TwoOpt)
^^^^^^^^^^^^^^

.. image:: https://img.shields.io/badge/Variable-permutation-blue.svg
.. image:: https://img.shields.io/badge/Objective-any-orange.svg
.. image:: https://img.shields.io/badge/Constraints-None-green.svg

.. autoclass:: flopt.solvers.two_opt.TwoOpt


Steepest Descent Search (SteepestDescentSearch)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: https://img.shields.io/badge/Variable-number-blue.svg
.. image:: https://img.shields.io/badge/Objective-polynominal-orange.svg
.. image:: https://img.shields.io/badge/Constraints-None-green.svg

.. autoclass:: flopt.solvers.steepest_descent.SteepestDescentSearch

Here is an example for visualization of optimization of :math:`f(x) = 2 x_0^2 + x_1^2 + x_0x_1``.

We prepare the callback function for saving the search points.

.. code-block:: python

    path = [[x[0].value(), x[1].value()]]
    def callback(solutions):
        path.append(solutions[0].value())

Then, we specify this to the callbacl argument of the Problem.solve().

.. code-block:: python

    status, log = prob.solve(solver, msg=True, timelimit=1, callback=callback)

Finally, we visualize the search path.

.. code-block:: python

    import flopt

    x = flopt.Variable.array("x", 2, cat="Continuous")
    x[0].setValue(1.5)
    x[1].setValue(1.0)

    def f(x):
        return 2*x[0]**2 + x[1]**2 + x[0]*x[1]

    prob = flopt.Problem()
    prob += f(x)

    path = [[x[0].value(), x[1].value()]]
    def callback(solutions):
        path.append(solutions[0].value())

    solver = flopt.Solver("SteepestDescentSearch")
    solver.setParams(xi=0.9, tau=0.9)
    status, log = prob.solve(solver, msg=True, timelimit=1, callback=callback)


    import numpy as np
    import matplotlib.pyplot as plt

    X = Y = np.linspace(-2, 2, 21)
    X_mesh, Y_mesh = np.meshgrid(X, Y)
    Z = f(np.array((X_mesh, Y_mesh)))

    fig, ax = plt.subplots()
    cmap = plt.get_cmap("tab10")
    color_i = 0

    ax.contour(X, Y, Z, levels=np.logspace(-0.3, 1.2, 10))
    path = np.array(path)
    ax.plot(path[:,0], path[:,1], marker="o", linestyle="--", color=cmap(0), zorder=1)
    ax.scatter(path[0, 0], path[0, 1], marker="o", color=cmap(1), label="initial point", zorder=2)
    ax.scatter(path[-1, 0], path[-1, 1], marker="o", color=cmap(6), label="final point", zorder=2)
    ax.set_aspect('equal')
    ax.grid("--")
    ax.legend()


.. image:: https://cdn-ak.f.st-hatena.com/images/fotolife/i/inarizuuuushi/20221106/20221106104712.png


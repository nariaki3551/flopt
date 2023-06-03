Coordinate Descent
==================

Coordinate Descent is a kind of iterative optimization algorithm. This method dose not update all variables but a part of variables in one step.
In this example, we minimize :math:`f(x_0, x_1) = 2 x_0^2 + x_1^2 + x_0x_1`.
By using optimized_variables option, we select the update variables in one optimization.


.. code-block:: python

    import flopt

    x = flopt.Variable.array("x", 2, cat="Continuous")
    x[0].setValue(1.5)
    x[1].setValue(1.0)

    # objective function
    def f(x):
        return 2*x[0]**2 + x[1]**2 + x[0]*x[1]
        
    
    prob = flopt.Problem()
    prob += f(x)

    # store variable path
    path = [[x[0].value(), x[1].value()]]
    def callback(*args, **kwargs):
        path.append([x[0].value(), x[1].value()])
    

    # Coordinate Descent
    options = dict(timelimit=0.1, callbacks=[callback])
    for _ in range(10):
        # optimize only x_0
        status, log = prob.solve(optimized_variables=[x[0]], **options)
        # optimize only x_1
        status, log = prob.solve(optimized_variables=[x[1]], **options)
    

    # plot
    import numpy as np
    import matplotlib.pyplot as plt
    
    X = Y = np.linspace(-2, 2, 21)
    X_mesh, Y_mesh = np.meshgrid(X, Y)
    Z = f(np.array((X_mesh, Y_mesh)))
    
    fig, ax = plt.subplots()
    cmap = plt.get_cmap("tab10")
    
    ax.contour(X, Y, Z, levels=np.logspace(-0.3, 1.2, 10))
    path = np.array(path)
    ax.plot(path[:,0], path[:,1], marker="o", linestyle="--", color=cmap(0), zorder=1)
    ax.scatter(path[0, 0], path[0, 1], marker="o", color=cmap(1), label="initial point", zorder=2)
    ax.scatter(path[-1, 0], path[-1, 1], marker="o", color=cmap(6), label="final point", zorder=2)
    ax.set_aspect('equal')
    ax.grid("--")
    ax.legend()

The solution path is here. x0 and x1 were updated alternately.

.. image:: https://cdn-ak.f.st-hatena.com/images/fotolife/i/inarizuuuushi/20221120/20221120135934.png

For reference, this plot shows the solution path of the standard steepese descent algorithm.

.. image:: https://cdn-ak.f.st-hatena.com/images/fotolife/i/inarizuuuushi/20221120/20221120135929.png

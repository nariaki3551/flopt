Obtain Multiple Solutions
=========================


.. code-block:: python

    from flopt import Variable, Problem, Solver

    # Variables
    a = Variable('a', lowBound=0, upBound=1, cat='Integer')
    b = Variable('b', lowBound=1, upBound=2, cat='Continuous')
    c = Variable('c', lowBound=1, upBound=3, cat='Continuous')

    # 1. Minimize
    prob = Problem(name='Test')

    import numpy as np
    x = np.array([a, b, c], dtype=object)
    J = np.array([
        [1, 2, 1],
        [0, 1, 1],
        [0, 0, 3]
    ])
    h = np.array([1, 2, 0])
    prob += - (x.T).dot(J).dot(x) - (h.T).dot(x)


When we want to obtain multiple solutions, not just the best solution,
we set `max_k` parameter to solver.

.. code-block:: python

    solver = Solver('RandomSearch')
    solver.setParams(max_k=2, timelimit=1)

Then, we solve.

.. code-block:: python

    prob.solve(solver, msg=True)

    >>> Welcome to the flopt Solver
    >>> Version 0.3
    >>> Date: July 3, 2021
    >>>
    >>> Algorithm: RandomSearch
    >>> Params: {'timelimit': 1}
    >>> Number of variables 3 (continuous 2 , int 1, binary 0, permutation 0 (0))
    >>>
    >>>
    >>>      Trial Incumbent    BestBd  Gap[%] Time[s]
    >>> ----------------------------------------------
    >>> S        0   -20.250         -       -    0.01
    >>> *        9   -20.851         -       -    0.01
    >>> *       10   -29.206         -       -    0.01
    >>> *       13   -35.924         -       -    0.01
    >>> *       18   -36.384         -       -    0.01
    >>> *       21   -37.656         -       -    0.01
    >>> *       25   -45.219         -       -    0.01
    >>> *       53   -46.113         -       -    0.02
    >>> *      181   -48.142         -       -    0.02
    >>> *      541   -48.301         -       -    0.04
    >>> *     1864   -49.112         -       -    0.08
    >>> *     7668   -49.855         -       -    0.21
    >>>
    >>> Status: timelimit termination
    >>> Objective Value: -49.855399194203244
    >>> Time: 1.0000581741333008


And we can obtain and set k-th solution to variables by
`getSolution` and `setSolution`.

.. code-block:: python

    from itertools import count
    for k in count(0):
        try:
            solution = prob.getSolution(k=k)
            prob.setSolution(k=k)
        except KeyError:
            break
        var_dict = solution.toDict()
        print(f'{k:2d}-th obj = {prob.obj.value():.4f}',
              {name: f'{var.value():.4f}' for name, var in var_dict.items()})

    >>>  0-th obj = -49.8283 {'a': '1.0000', 'b': '1.9955', 'c': '2.9942'}
    >>>  1-th obj = -49.7413 {'a': '1.0000', 'b': '1.9793', 'c': '2.9985'}
    >>>  2-th obj = -49.4444 {'a': '1.0000', 'b': '1.9629', 'c': '2.9929'}
    >>>  3-th obj = -49.3430 {'a': '1.0000', 'b': '1.9763', 'c': '2.9810'}
    >>>  4-th obj = -49.3113 {'a': '1.0000', 'b': '1.9664', 'c': '2.9847'}
    >>>  5-th obj = -49.2906 {'a': '1.0000', 'b': '1.9592', 'c': '2.9875'}
    >>>  6-th obj = -49.2228 {'a': '1.0000', 'b': '1.9396', 'c': '2.9944'}
    >>>  7-th obj = -48.7660 {'a': '1.0000', 'b': '1.9838', 'c': '2.9493'}
    >>>  8-th obj = -47.4232 {'a': '1.0000', 'b': '1.9985', 'c': '2.8759'}
    >>>  9-th obj = -46.0485 {'a': '1.0000', 'b': '1.7550', 'c': '2.9360'}
    >>> 10-th obj = -45.8896 {'a': '1.0000', 'b': '1.9013', 'c': '2.8516'}
    >>> 11-th obj = -44.3446 {'a': '1.0000', 'b': '1.8565', 'c': '2.7977'}
    >>> 12-th obj = -41.8523 {'a': '1.0000', 'b': '1.8011', 'c': '2.6985'}
    >>> 13-th obj = -38.8659 {'a': '1.0000', 'b': '1.8580', 'c': '2.5049'}
    >>> 14-th obj = -37.9598 {'a': '1.0000', 'b': '1.8075', 'c': '2.4828'}
    >>> 15-th obj = -34.9277 {'a': '0.0000', 'b': '1.4278', 'c': '2.9350'}


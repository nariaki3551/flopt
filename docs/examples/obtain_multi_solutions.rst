Obtain Multiple Solutions
=========================


.. code-block:: python

    import numpy as np
    from flopt import Variable, Problem, Solver

    # Variables
    a = Variable("a", lowBound=0, upBound=1, cat="Integer")
    b = Variable("b", lowBound=1, upBound=2, cat="Continuous")
    c = Variable("c", lowBound=1, upBound=3, cat="Continuous")

    # 1. Minimize
    prob = Problem(name="Test")

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

    solver = Solver("RandomSearch")
    solver.setParams(max_k=8, timelimit=3)

Then, we solve.

.. code-block:: python

    prob.solve(solver, msg=True)


    >>> # - - - - - - - - - - - - - - #
    >>>   Welcome to the flopt Solver
    >>>   Version 0.5.4
    >>>   Date: September 1, 2022
    >>> # - - - - - - - - - - - - - - #
    >>> 
    >>> Algorithm: RandomSearch
    >>> Params: {'timelimit': 3}
    >>> Number of variables 3 (continuous 2 , int 1, binary 0, spin 0, permutation 0 (0))
    >>> 
    >>> 
    >>>                                relative  absolute
    >>>      Trial Incumbent    BestBd   Gap[%]       Gap Time[s]
    >>> ---------------------------------------------------------
    >>> S        0   -23.424         -        -         -    0.00
    >>> *        5   -30.484         -        -         -    0.00
    >>> *       14   -34.383         -        -         -    0.00
    >>> *       60   -42.098         -        -         -    0.00
    >>> *       76   -43.724         -        -         -    0.00
    >>> *      169   -44.827         -        -         -    0.01
    >>> *      175   -45.373         -        -         -    0.01
    >>> *      273   -48.962         -        -         -    0.01
    >>> *     2993   -49.877         -        -         -    0.08
    >>> 
    >>> Status: timelimit termination
    >>> Objective Value: -49.876980561739174
    >>> Time: 3.000058889389038
    >>>     Build Time: 0.0
    >>>     Search Time: 3.000058889389038


After that, we can obtain and set k-th solution to variables by
`getSolution` and `setSolution` api of Problem.

.. code-block:: python

    from itertools import count
    for k in count(1):
        try:
            solution = prob.getSolution(k=k)
            prob.setSolution(k=k)
        except IndexError:
            break
        var_dict = solution.toDict()
        print(f"{k:2d}-th obj = {prob.obj.value():.4f}",
              {name: f"{var.value():.4f}" for name, var in var_dict.items()})

    >>>  1-th obj = -49.8770 {'a': '1.0000', 'b': '1.9894', 'c': '2.9997'}
    >>>  2-th obj = -48.9620 {'a': '1.0000', 'b': '1.9384', 'c': '2.9825'}
    >>>  3-th obj = -45.3729 {'a': '1.0000', 'b': '1.8632', 'c': '2.8460'}
    >>>  4-th obj = -44.8267 {'a': '1.0000', 'b': '1.7706', 'c': '2.8674'}
    >>>  5-th obj = -43.7245 {'a': '1.0000', 'b': '1.6107', 'c': '2.8943'}
    >>>  6-th obj = -42.0979 {'a': '1.0000', 'b': '1.6277', 'c': '2.8031'}
    >>>  7-th obj = -34.3833 {'a': '1.0000', 'b': '1.9070', 'c': '2.2126'}
    >>>  8-th obj = -30.4840 {'a': '1.0000', 'b': '1.2035', 'c': '2.3790'}


Sudoku
======

We will solver a following sudoku puzzle.

::

        0 1 2   3 4 5   6 7 8
      +-------+-------+-------+
   0  |       |       |   1   |
   1  | 4     |       |       |
   2  |   2   |       |       |
      +-------+-------+-------+
   3  |       |   5   | 4   7 |
   4  |     8 |       | 3     |
   5  |     1 |   9   |       |
      +-------+-------+-------+
   6  | 3     | 4     | 2     |
   7  |   5   | 1     |       |
   8  |       | 8   6 |       |
      +-------+-------+-------+


We represent this problem as following dictionary.


.. code-block:: python

    # problem format
    hints = [
        # value, row, col
        (1, 0, 7), (4, 1, 0), (2, 2, 1),
        (5, 3, 4), (4, 3, 6), (7, 3, 8),
        (8, 4, 2), (3, 4, 6), (1, 5, 2),
        (9, 5, 4), (3, 6, 0), (4, 6, 3),
        (2, 6, 6), (5, 7, 1), (1, 7, 3),
        (8, 8, 3), (6, 8, 5),
    ]


.. code-block:: python

    # A list of number sequence
    Sequence = list(range(9))
    Vals = Sequence
    Rows = Sequence
    Cols = Sequence


We create Binary variables :math:`x_{ijk}` such that
:math:`x_{ijk} = 1` if :math:`j`-row and :math:`k`-column piece's value is :math:`i` else :math:`x_{ijk} = 0`.

.. code-block:: python

    from flopt import Variable

    # The problem variables
    x = Variable.array("x", (9, 9, 9), cat='Binary', ini_value=0)


Following given hints, we replace some variable for constants.

.. code-block:: python

    from flopt import Const

    # The starting numbers are entered as constant
    for value, row, col in hints:
        x[value-1, row, col] = Const(1)


Then, we create Problem.

.. code-block:: python

    from flopt import Problem, Sum

    prob = Problem("Sudoku")

    # A constraint ensuring that only one value can be in each piece
    for r in Rows:
        for c in Cols:
            prob += Sum(x[:, r, c]) == 1  # is equal to Sum(x[i, r, c] for i in Vals) == 1

    # The row, column and box constraints are added for each value
    for v in Vals:
        for r in Rows:
            prob += Sum(x[v, r, :]) == 1

        for c in Cols:
            prob += Sum(x[v, :, c]) == 1

        for r in [0, 3, 6]:
            for c in [0, 3, 6]:
                prob += Sum(x[v, r:r+3, c:c+3]) == 1


We solve this problem using `AutoSolver`.

.. code-block:: python

    from flopt import Solver

    solver = Solver('auto')
    prob.solve(solver, msg=True)
    >>> Welcome to the flopt Solver
    >>> Version 0.4
    >>> Date: August 12, 2021

    >>> Algorithm: PulpSearch
    >>> Params: {'timelimit': inf}
    >>> Number of variables 712 (continuous 0 , int 0, binary 712, permutation 0 (0))


    >>>      Trial Incumbent    BestBd  Gap[%] Time[s]
    >>> ----------------------------------------------
    >>> S        0       inf         -       -    0.00

    >>> Status: normal termination
    >>> Objective Value: 0
    >>> Time: 0.07421302795410156
    >>> Out[15]:
    >>> (<SolverTerminateState.Normal: 0>,
    >>>  <flopt.solvers.solver_utils.solver_log.Log at 0x12b42de20>)


The result is as follows.

.. code-block:: python

   from flopt import Value

    # display result
    row_line = "+-------+-------+-------+"
    print(row_line)
    for r in Rows:
        if r in {3, 6}:
            print(row_line)
        for c in Cols:
            if c in {0, 3, 6}:
                print("| ", end='')
            for v in Vals:
                if Value(x[v, r, c]) == 1:
                    print(f'{v+1} ', end='')
            if c == 8:
                print("|")
    print(row_line)


::

    +-------+-------+-------+
    | 6 9 3 | 7 8 4 | 5 1 2 |
    | 4 8 7 | 5 1 2 | 9 3 6 |
    | 1 2 5 | 9 6 3 | 8 7 4 |
    +-------+-------+-------+
    | 9 3 2 | 6 5 1 | 4 8 7 |
    | 5 6 8 | 2 4 7 | 3 9 1 |
    | 7 4 1 | 3 9 8 | 6 2 5 |
    +-------+-------+-------+
    | 3 1 9 | 4 7 5 | 2 6 8 |
    | 8 5 6 | 1 2 9 | 7 4 3 |
    | 2 7 4 | 8 3 6 | 1 5 9 |
    +-------+-------+-------+



In addition, you can obtain the objective vector and constraints matrix of this problem, as follows.

::

    obj  c.T.dot(x) + C
    s.t. Gx <= h
         Ax == b
         lb <= x <= ub


.. code-block:: python

    from flopt.convert import LpStructure
    lp = LpStructure.fromFlopt(prob)

    print(lp)
    >>> LpStructure
    >>>   #variable 712
    >>>   #c  (712,)
    >>>   #C  0
    >>>   #G  None  (0-element None %)
    >>>   #h  None
    >>>   #A  (324, 712)  (0-element 98.765 %)
    >>>   #b  (324,)
    >>>   #lb 712
    >>>   #ub 712

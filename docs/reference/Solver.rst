Solver
======

.. autofunction:: flopt.Solver

.. autofunction:: flopt.Solver_list

.. autoclass:: flopt.solvers.base.BaseSearch
  :members:



.. module:: flopt.solvers

BlackBox Solver
---------------

Swarm Intelligence Search
^^^^^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: ShuffledFrogLeapingSearch
  :members:

Sequential Update Search
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: SequentialUpdateSearch
  :members:

**Sampling Search**

.. autoclass:: RandomSearch
  :members:


**Sampling Search using Optuna**


.. autoclass:: OptunaTPESearch
  :members:

.. autoclass:: OptunaCmaEsSearch
  :members:


**Sampling Search using Hyperopt**

.. autoclass:: HyperoptTPESearch

Permutation Solver
------------------
.. autoclass:: TwoOpt
  :members:

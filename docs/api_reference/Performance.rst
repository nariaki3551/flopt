Performance
===========

User Interface
--------------

.. module:: flopt.performance

.. autofunction:: compute

.. autoclass:: LogVisualizer
   :members:


.. autoclass:: CustomDataset
   :members:

Datasets
--------

.. autoclass:: BaseDataset
   :members:

.. autoclass:: TSPDataset
   :members:

.. autoclass:: FuncDataset
   :members:


External Interface
------------------

Compute and view the performance of (dataset, algo).

Compute Performance
^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

  python compute_performance.py algo save_algo_name --datasets datasetA datasetB  --params param_file

- algo is the algorithm, we select algorithm from `flopt.Solver_list()`.
- The result of compute the performance is save in ./performance/save_algo_name/dataset_name/instance_name/log.pickle.
- dataset can be select from `flopt.Dataset_list()`.
- param_file's format is `parameter = value`, for example, as follows.

::

  n_trial = 10000
  timelimit = 30

Example for running the script.

.. code-block:: bash

  python compute_performance.py 2-Opt 2-Opt_timelimit30 --datasets tsp  --params default.param
  python compute_performance.py RandomSearch RandomSearch_iteration100  --datasets tsp  --params default.param
  python compute_performance.py OptunaCmaEsSearch OptunaCmaEsSearch --datasets func --params default.param

.. autofunction:: compute_performance.compute


View Performance
^^^^^^^^^^^^^^^^

.. code-block:: bash

  python view_performance.py --algo algoA algoB  --datasets datasetA datasetB
  python view_performance.py --algo algoA algoB  --datasets datasetA datasetB --xitem iteration

- The result of compute the performance is save in ./performance/algo/dataset_name/instance_name/log.pickle.
- dataset can be select from `flopt.Dataset_list()`.
- xitem can be choised from 'time' or 'instance'.

Example for running the script.

.. code-block:: bash

  python view_performance.py --algo 2-Opt_timelimit30
  python view_performance.py -- datasets tsp

.. autofunction:: view_performance.view_performance

.. autofunction:: performance


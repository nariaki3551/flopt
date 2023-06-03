.. flopt documentation master file, created by
   sphinx-quickstart on Sat Apr  4 00:07:04 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

flopt: A flexible modeler for optimization problems
===================================================

flopt is a modeling tool for optimization problems such as LP, QP, Ising, QUBO, etc. 
flopt provides various functions for flexible and easy modeling.
Users can also solve modeled problems with several solvers to obtain optimal or good solutions.

Key Features
------------

flopt has functionalities as follows:

- Intuitive user interface and flexible mathematical expression supporting nonlinear, linear, polynomial, and black box functions

  - :doc:`tutorial/modeling_and_solving`
  - :doc:`tutorial/expression_examples`

- Automatic linearization of variable products and conversion to equation or inequation standard form of linear programming models

  - :doc:`api_reference/convert/linearize`
  - :doc:`tutorial/convert/lp`

- Function to convert to other problem representation formats (e.g., from ising model to quadratic programming)

  - :doc:`tutorial/convert/overview`

- Problem estimation and automatic solver selection functions.

  - :doc:`tutorial/problem_type`
  - :doc:`solvers/Auto`


.. toctree::
   :maxdepth: 1
   :caption: Contents:

   installation
   tutorial/index
   case_studies/index
   solvers/index
   api_reference/index
   reference/index
   recipes/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

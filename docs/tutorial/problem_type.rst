Estimation of Problem type
==========================

Flopt includes problem estimation mechanism, and provide an API for user to see the user defined problem type.


.. code-block:: python

  import flopt

  x = flopt.Variable("x")
  y = flopt.Variable("y")
  
  prob = flopt.Problem()
  
  prob += x + y
  flopt.estimate_problem_type(prob)
  >>> Problem
  >>> 	Name: None
  >>> 	  Type         : Problem
  >>> 	  sense        : Minimize
  >>> 	  objective    : x+y
  >>> 	  #constraints : 0
  >>> 	  #variables   : 2 (Continuous 2)
  >>> 
  >>> Problem components
  >>> 	Variable: Continuous
  >>> 	Objective: Linear
  >>> 	Constraint: Non
  >>> 
  >>> Problem classes
  >>> 	--> lp
  >>> 	--> mip
  >>> 	    ising
  >>> 	--> quadratic
  >>> 	    permutation
  >>> 	    blackbox
  >>> 	    blackbox with interger variables
  >>> 	--> nonlinear
  >>> 	--> nonlinear with integer variables


Flopt characterize the problem with (variable type, objective, constraints). These element are defined https://github.com/nariaki3551/flopt/blob/373fd556266404c3e0e92429ea3d2934cf6c7b92/flopt/constants.py#L46-L104 . In addition, optimization problem types are defined in https://github.com/nariaki3551/flopt/blob/373fd556266404c3e0e92429ea3d2934cf6c7b92/flopt/solvers/auto_search/selector.py#L51-L109 .

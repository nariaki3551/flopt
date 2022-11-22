# flopt

A Python Flexible Modeler for Optimization Problems.<br><br>

flopt is a modeling tool for optimization problems such as LP, QP, Ising, QUBO, etc.
flopt provides various functions for flexible and easy modeling.
Users can also solve modeled problems with several solvers to obtain optimal or good solutions.

[![Documentation Status](https://readthedocs.org/projects/flopt/badge/?version=latest)](https://flopt.readthedocs.io/en/latest/?badge=latest) [![PyPI version](https://badge.fury.io/py/flopt.svg)](https://badge.fury.io/py/flopt) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/flopt) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

[documentation](https://flopt.readthedocs.io/en/latest/) | [tutorial](https://flopt.readthedocs.io/en/latest/tutorial/index.html) | [case studies](https://flopt.readthedocs.io/en/latest/case_studies/index.html)

<br>

## Install

**PyPI**

```
pip install flopt
```

**GitHub**

```
git clone https://github.com/flab-coder/flopt.git
cd flopt && python -m pip install .
```

<br>

## Formulatable problems in flopt

- Linear Programming (LP)
- Quadratic Programming (QP)
- Ising
- Quadratic Unconstrainted Binary Programming  (QUBO)
- Non-Linear problem
  ```
  minimize  2*(3*a+b)*c**2 + 3
  s.t       a + b * c <= 3
            0 <= a <= 1
            1 <= b <= 2
                 c <= 3
  ```
- BlackBox problem
  ```
  minimize  simulator(a, b, c)
  s.t       0 <= a <= 1
            1 <= b <= 2
            1 <= c <= 3
  ```
- Finding the best permutation problem (including TSP)
- Satisfiability problem (including MAX-SAT)

<br>

## Available Solvers and Heuristic Algorithms

- CBC, CVXOPT, scipy.optimize(minimize, linprog, milp), Optuna
- Random Search, 2-Opt, Swarm Intelligence Search

<br>

## Simple Example

You  can write codes like PuLP application.

```python
from flopt import Variable, Problem

# Variables
a = Variable('a', lowBound=0, upBound=1, cat='Continuous')
b = Variable('b', lowBound=1, upBound=2, cat='Continuous')
c = Variable('c', upBound=3, cat='Continuous')

# Problem
prob = Problem()
prob += 2 * (3*a+b) * c**2 + 3 # set the objective function
prob += a + b * c <= 3         # set the constraint

# Solve
prob.solve(timelimit=0.5, msg=True) # run solver to solve the problem

# display the result, incumbent solution
print('obj value', prob.getObjectiveValue())
print('a', a.value())
print('b', b.value())
print('c', c.value())
```

<br>

In addition, you can represent any objective function by *CustomExpression*

```python
from flopt import Variable, Problem, CustomExpression

# Variables
a = Variable('a', lowBound=0, upBound=1, cat='Integer')
b = Variable('b', lowBound=1, upBound=2, cat='Continuous')

def user_func(a, b):
    from math import sin, cos
    return (0.7*a + 0.3*cos(b)**2 + 0.1*sin(b))*abs(a)

custom_obj = CustomExpression(func=user_func, args=[a, b])

prob = Problem(name='CustomExpression')
prob += custom_obj

# Solve
prob.solve(timelimit=1, msg=True)  # run solver to solve the problem

# display the result, incumbent solution
print('obj value', prob.getObjectiveValue())
```

<br>

In the case you solve TSP, *Permutation Variable* is useful.

```python
from flopt import Variable, Problem, CustomExpression

N = 4  # Number of city
D = [[0,1,2,3],  # Distance matrix
     [3,0,2,1],
     [1,2,0,3],
     [2,3,1,0]]

# Variables
x = Variable('x', lowBound=0, upBound=N-1, cat='Permutation')

# Object
def tsp_dist(x):
    distance = 0
    for head, tail in zip(x, x[1:]+[x[0]]):
        distance += D[head][tail]  # D is the distance matrix
    return distance
tsp_obj = CustomExpression(func=tsp_dist, args=[x])

# Problem
prob = Problem(name='TSP')
prob += tsp_obj

# Solve
prob.solve(timelimit=10, msg=True)    # run solver to solve the problem

# display the result, incumbent solution
print('obj value', prob.getObjectiveValue())
print('x', x.value())
```

## Learning more

- document: https://flopt.readthedocs.io/en/latest/
- tutorials: https://flopt.readthedocs.io/en/latest/tutorial/index.html
- case studies: https://flopt.readthedocs.io/en/latest/case_studies/index.html


# flopt

A python Non-Linear Programming API with Heuristic approach.

[![Documentation Status](https://readthedocs.org/projects/flopt/badge/?version=latest)](https://flopt.readthedocs.io/en/latest/?badge=latest) [![PyPI version](https://badge.fury.io/py/flopt.svg)](https://badge.fury.io/py/flopt) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/flopt) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

[docs](https://flopt.readthedocs.io/en/latest/) | [tutorial](https://flopt.readthedocs.io/en/latest/tutorial/index.html)

<br>

## Install

**PyPI**

```
pip install flopt
```

**GitHub**

```
git clone https://github.com/flab-coder/flopt.git
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

- Finding the best permutation problem ( including TSP)

- Satisfiability problem (including MAX-SAT)

<br>

## Heuristic Algorithms

- Random Search
- 2-Opt
- Swarm Intelligence Search
- Other applications

<br>

## Simple Example

You  can write codes like PuLP application.

```python
from flopt import Variable, Problem, Solver

# Variables
a = Variable('a', lowBound=0, upBound=1, cat='Continuous')
b = Variable('b', lowBound=1, upBound=2, cat='Continuous')
c = Variable('c', upBound=3, cat='Continuous')

# Problem
prob = Problem()
prob += 2 * (3*a+b) * c**2 + 3 # set the objective function
prob += a + b * c <= 3         # set the constraint

# Solver
solver = Solver(algo='ScipySearch')  # select the heuristic algorithm
solver.setParams(n_trial=1000)  # setting of the hyper parameters
prob.solve(solver, msg=True)    # run solver to solve the problem

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

from math import sin, cos
def user_func(a, b):
    return (0.7*a + 0.3*cos(b)**2 + 0.1*sin(b))*abs(a)

custom_obj = CustomExpression(func=user_func, variables=[a, b])

prob = Problem(name='CustomExpression')
prob += custom_obj

# Solver
solver = Solver(algo='RandomSearch')  # select the heuristic algorithm
solver.setParams(n_trial=1000)  # setting of the hyper parameters
prob.solve(solver, msg=True)    # run solver to solve the problem

# display the result, incumbent solution
print('obj value', prob.getObjectiveValue())
print('a', a.value())
print('b', b.value())
```

<br>

In the case you solve TSP, *Permutation Variable* is useful.

```python
from flopt import Variable, Problem, Solver

N = 4
D = [[0,1,2,3],
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
tsp_obj = CustomExpression(func=tsp_dist, variables=[x])

# Problem
prob = Problem(name='TSP')
prob += tsp_obj

# Solver
solver = Solver(algo='2-Opt')  # select the heuristic algorithm
solver.setParams(n_trial=1000)  # setting of the hyper parameters
prob.solve(solver, msg=True)    # run solver to solve the problem

# display the result, incumbent solution
print('obj value', prob.getObjectiveValue())
print('x', x.value())
```




# flopt



### version 0.3 (3 July, 2021)

**Update**

1. available() and allAvailableSolvers() can be useable
   1. `solver.available(prob)`
   2. `allAvailableSolvers(prob)`
2. Add new solvers
   1. `AutoSearch`
      1. Select appropriate solvers by givin problem and setting
3. Add `isLinear` `isIsing` `toIsing` `maxDegree` function in Problem
4. `import flopt` is 4 times faster
5. Fix some bugs about `view_performance.py`




### version 0.2 (30 May, 2020)

**Update**

1. Constraints can be useable
   1. `prob += a + b <= c + 2`
2. Add new solvers
   1. `PulpSearch`
      1. PulpSearch can solve LP with constraints.
   2. `ScipySearch`
      1. ScipySearch can solve non-linear programming with constraints, and black-box optimization problem with constraints.
3. Update the performance viewing
4. Add a lot of benchmarking functions
5. Add logging function
   1. change log level by `flopt.env.setLevel(10)`.

**API Change**

#### API Change

1. CustomObject → CustomExpression



### version0.1 (30 Apr, 2020)

1. Available Solvers are RandomSearch, 2-Opt, OptunaTPESearch, OptunaCmaEsSearch, HyperoptTPESearch

